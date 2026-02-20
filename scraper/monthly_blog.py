"""
네이버 이달의 블로그 수집 스크립트
Playwright를 사용하여 동적 페이지에서 블로그 정보를 수집합니다.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright


def extract_blog_id(url: str) -> str:
    """블로그 URL에서 ID 추출"""
    # https://blog.naver.com/blogId 형태
    match = re.search(r'blog\.naver\.com/([^/?]+)', url)
    if match:
        blog_id = match.group(1)
        # 시스템 페이지 제외
        system_pages = [
            'BlogHome.naver', 'MyBlog.naver', 'market', 'blogpeople',
            'ThemePost.naver', 'DirectoryPost.naver', 'SearchBlog.naver',
            'PostList.naver', 'PostView.naver', 'prologue', 'ThisMonthDirectory.naver'
        ]
        if blog_id in system_pages or blog_id.endswith('.naver'):
            return ""
        return blog_id
    return ""


def get_monthly_blogs(headless: bool = True, year: int = None, month: int = None) -> dict:
    """
    네이버 이달의 블로그 목록 수집

    Args:
        headless: 브라우저 헤드리스 모드
        year: 수집할 년도 (기본값: 현재 년도)
        month: 수집할 월 (기본값: 현재 월, 없으면 이전 월)

    Returns:
        dict: {"month_title": "2026년 1월", "blogs": [...]}
    """
    blogs = []
    month_title = ""

    # 기본값: 현재 년/월
    now = datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        try:
            # 이달의 블로그 페이지 URL
            url = f"https://section.blog.naver.com/ThisMonthDirectory.naver?month={month}&year={year}"
            print(f"수집 URL: {url}")

            page.goto(url, timeout=30000)
            page.wait_for_load_state("networkidle", timeout=15000)

            # 페이지 끝까지 스크롤하여 lazy loading 콘텐츠 로드
            prev_height = 0
            for _ in range(15):  # 최대 15회 스크롤
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(800)  # 콘텐츠 로드 대기 (늘림)
                curr_height = page.evaluate("document.body.scrollHeight")
                if curr_height == prev_height:
                    break
                prev_height = curr_height

            # 추가로 한번 더 대기 후 스크롤
            page.wait_for_timeout(1000)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)

            # 맨 위로 다시 스크롤 (bounding_box 계산을 위해)
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(500)

            # 페이지 제목에서 월 정보 확인
            title_el = page.query_selector(".tit_month, .month_title, h2.tit, .section_title")
            if title_el:
                title_text = title_el.inner_text().strip()
                match = re.search(r'(\d{4}년\s*\d{1,2}월)', title_text)
                if match:
                    month_title = match.group(1)

            # 월 정보가 없으면 URL 파라미터 기준으로 설정
            if not month_title:
                month_title = f"{year}년 {month}월"

            print(f"기준 월: {month_title}")

            # 블로거 카드 목록 수집 (네이버 이달의 블로그 페이지 구조)
            # 주제별 섹션으로 구성됨: h4.directory_title > 블로거 목록

            # 주제 섹션 찾기
            sections = page.query_selector_all("[class*='popularblog_list_wrap'], [class*='directory_area'], section, article")

            # 주제별로 블로거 수집
            current_topic = ""

            # 먼저 모든 주제 제목 위치 파악
            topic_elements = page.query_selector_all("[class*='directory_title']")
            topic_positions = []
            for topic_el in topic_elements:
                topic_text = topic_el.inner_text().strip()
                # "만화·애니 5" 형태에서 숫자 제거
                topic_name = re.sub(r'\s*\d+$', '', topic_text).strip()
                if topic_name:
                    # 요소의 위치 정보
                    box = topic_el.bounding_box()
                    if box:
                        topic_positions.append({
                            "name": topic_name,
                            "y": box["y"]
                        })

            print(f"주제 섹션: {[t['name'] for t in topic_positions]}")

            # 블로거 카드 수집
            cards = page.query_selector_all("[class*='item_inner']")
            print(f"Found {len(cards)} blogger cards")

            for card in cards:
                try:
                    # 블로그 링크 찾기 (profile_image 내 링크)
                    link_el = card.query_selector("[class*='profile_image'] a[href*='blog.naver.com']")
                    if not link_el:
                        link_el = card.query_selector("a[href*='blog.naver.com']")
                    if not link_el:
                        continue

                    href = link_el.get_attribute("href")
                    blog_id = extract_blog_id(href) if href else ""
                    if not blog_id or blog_id in [b["id"] for b in blogs]:
                        continue

                    # 카드 위치로 주제 결정
                    card_box = card.bounding_box()
                    topic = ""
                    if card_box and topic_positions:
                        card_y = card_box["y"]
                        # 카드보다 위에 있는 가장 가까운 주제 찾기
                        for tp in reversed(topic_positions):
                            if tp["y"] < card_y:
                                topic = tp["name"]
                                break

                    # 닉네임 추출
                    nick_el = card.query_selector("[class*='nickname']")
                    nickname = nick_el.inner_text().strip() if nick_el else ""

                    # 블로그명 추출
                    blogname_el = card.query_selector("[class*='blogname']")
                    blogname = blogname_el.inner_text().strip() if blogname_el else ""

                    # 소개글 추출
                    intro_el = card.query_selector("[class*='introduce'] p")
                    intro = intro_el.inner_text().strip() if intro_el else ""

                    # 이름 결정 (닉네임 우선, 없으면 블로그명)
                    name = nickname or blogname or blog_id

                    blogs.append({
                        "id": blog_id,
                        "name": name,
                        "blogname": blogname,
                        "url": f"https://blog.naver.com/{blog_id}",
                        "topic": topic,
                        "intro": intro[:100] if intro else ""
                    })
                except Exception as e:
                    continue

            print(f"수집된 블로거: {len(blogs)}명")

            # 현재 월에 데이터가 없으면 이전 월 시도
            if not blogs and month == now.month:
                print(f"{month}월 데이터가 없음, {month-1}월 시도...")
                browser.close()
                prev_month = month - 1 if month > 1 else 12
                prev_year = year if month > 1 else year - 1
                return get_monthly_blogs(headless=headless, year=prev_year, month=prev_month)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

    return {"month_title": month_title, "year": year, "month": month, "blogs": blogs}


def save_monthly_blogs(result: dict, output_dir: str = ".") -> str:
    """수집된 블로그 목록을 JSON 파일로 저장"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"monthly_blogs_{timestamp}.json"
    filepath = Path(output_dir) / filename

    blogs = result.get("blogs", [])
    month_title = result.get("month_title", "")

    data = {
        "collected_at": datetime.now().isoformat(),
        "month_title": month_title,
        "year": result.get("year"),
        "month": result.get("month"),
        "count": len(blogs),
        "blogs": blogs
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return str(filepath)


if __name__ == "__main__":
    print("네이버 이달의 블로그 수집 중...")
    result = get_monthly_blogs(headless=True)

    blogs = result.get("blogs", [])
    month_title = result.get("month_title", "")

    if blogs:
        print(f"\n[{month_title}] 이달의 블로그")
        print(f"수집된 블로그: {len(blogs)}개\n")

        for i, blog in enumerate(blogs, 1):
            topic = f" [{blog.get('topic')}]" if blog.get('topic') else ""
            print(f"{i}. {blog['id']}{topic} - {blog['name']}")

        # 저장
        filepath = save_monthly_blogs(result, "output")
        print(f"\n저장 완료: {filepath}")
    else:
        print("블로그를 찾지 못했습니다.")
