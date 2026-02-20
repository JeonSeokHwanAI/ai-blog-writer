"""
네이버 블로그 스크래퍼 - 메인 진입점

사용법:
    python main.py
"""

import os
import json
from scraper import NaverBlogScraper
from utils import save_posts_to_files

# 설정 파일 경로
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config", ".last_search.json")
OUTPUT_BASE = os.path.join(os.path.dirname(__file__), "output")


def load_last_search():
    """마지막 검색 정보 불러오기"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return None


def save_last_search(blog_id, output_dir):
    """마지막 검색 정보 저장"""
    data = {
        "blog_id": blog_id,
        "output_dir": output_dir
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extract_blog_id(user_input):
    """URL 또는 ID에서 블로그 ID 추출"""
    user_input = user_input.strip()

    # URL인 경우 ID 추출
    if "blog.naver.com" in user_input:
        # https://blog.naver.com/blogid 또는 https://blog.naver.com/blogid/포스트번호
        parts = user_input.replace("https://", "").replace("http://", "")
        parts = parts.split("/")
        if len(parts) >= 2:
            return parts[1].split("?")[0]  # 쿼리스트링 제거

    # 그냥 ID인 경우
    return user_input


def get_blog_output_dir(blog_id):
    """블로그 ID에 해당하는 출력 디렉토리 반환 (없으면 생성)"""
    blog_dir = os.path.join(OUTPUT_BASE, blog_id)
    os.makedirs(blog_dir, exist_ok=True)
    return blog_dir


def main():
    print("=" * 60)
    print("네이버 블로그 스크래퍼")
    print("=" * 60)
    print()

    # 마지막 검색 정보 표시
    last_search = load_last_search()
    if last_search:
        print(f"[최근 검색] {last_search['blog_id']}")
        print("  - 숫자만 입력하면 최근 검색한 블로그를 분석합니다.")
        print()

    # 블로그 ID 입력
    user_input = input(">> 블로그 ID 또는 URL (숫자만 입력시 최근 검색): ").strip()

    if not user_input:
        print("입력이 없습니다.")
        return

    # 숫자만 입력한 경우: 최근 검색한 블로그의 포스트 번호로 해석
    if user_input.isdigit() and last_search:
        blog_id = last_search["blog_id"]
        print(f"   최근 블로그 사용: {blog_id}")
        print(f"   포스트 번호: {user_input}")
        print()
        print(f">> {blog_id} 블로그의 {user_input}번 포스트를 분석하려면")
        print(f"   output/{blog_id}/ 폴더의 posts 파일을 참조하세요.")
        return

    blog_id = extract_blog_id(user_input)
    print(f"   블로그 ID: {blog_id}")
    print()

    # 검색 수 입력 (최소 1개, 최대 50개)
    limit_input = input(">> 검색할 포스트 수 (1~50, 기본 10): ").strip()
    if not limit_input:
        limit = 10
    else:
        try:
            limit = int(limit_input)
            if limit < 1:
                print("   최소 1개로 설정합니다.")
                limit = 1
            elif limit > 50:
                print("   최대 50개로 제한됩니다.")
                limit = 50
        except ValueError:
            print("   잘못된 입력입니다. 기본값 10으로 설정합니다.")
            limit = 10

    print()
    print("-" * 60)
    print(f"블로그를 체크합니다... (ID: {blog_id}, 수량: {limit}개)")
    print("-" * 60)
    print()

    # 스크래퍼 초기화 및 실행 (delay 기본값 0.3초)
    scraper = NaverBlogScraper(blog_id=blog_id)

    posts = scraper.scrape_all(
        limit=limit,
        include_content=True,
        include_images=True
    )

    if not posts:
        print("스크래핑된 포스트가 없습니다. 블로그 ID를 확인해주세요.")
        return

    # 블로그 ID별 폴더에 저장
    output_dir = get_blog_output_dir(blog_id)
    result = save_posts_to_files(posts, output_dir=output_dir, prefix=blog_id)

    # 마지막 검색 정보 저장
    save_last_search(blog_id, output_dir)

    print()
    print("=" * 60)
    print("완료!")
    print("=" * 60)
    print(f"총 포스트: {result['total']}개")
    print(f"저장 위치: {result['summary_file']}")
    print()


if __name__ == "__main__":
    main()
