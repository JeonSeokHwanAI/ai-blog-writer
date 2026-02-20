"""
네이버 블로그 스크래퍼 핵심 모듈
- RSS 피드로 포스트 목록 수집
- 모바일 버전으로 본문 추출
"""

import requests
import xml.etree.ElementTree as ET
import time
import re
from typing import Optional
from .parser import PostParser


class NaverBlogScraper:
    """네이버 블로그 스크래퍼"""

    # User-Agent 헤더
    DESKTOP_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    MOBILE_HEADERS = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
    }

    def __init__(self, blog_id: str, delay: float = 0.3):
        """
        Args:
            blog_id: 네이버 블로그 ID
            delay: 요청 간 딜레이 (초) - 기본 0.3초
        """
        self.blog_id = blog_id
        self.delay = delay
        self.parser = PostParser()
        # 연결 재사용을 위한 Session
        self.session = requests.Session()

    def get_post_list(self, limit: Optional[int] = None) -> list:
        """
        RSS 피드에서 포스트 목록 가져오기

        Args:
            limit: 가져올 포스트 수 (None이면 전체)

        Returns:
            포스트 목록 (제목, 링크, logNo, 날짜, 요약)
        """
        url = f"https://rss.blog.naver.com/{self.blog_id}.xml"

        try:
            response = self.session.get(url, headers=self.DESKTOP_HEADERS, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"RSS 요청 실패: {e}")
            return []

        # XML 파싱
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError as e:
            print(f"XML 파싱 실패: {e}")
            return []

        posts = []
        for item in root.findall(".//item"):
            post = {
                "title": "",
                "link": "",
                "logNo": "",
                "pubDate": "",
                "description": ""
            }

            # 제목
            title_elem = item.find("title")
            if title_elem is not None and title_elem.text:
                post["title"] = title_elem.text

            # 링크
            link_elem = item.find("link")
            if link_elem is not None and link_elem.text:
                post["link"] = link_elem.text
                # logNo 추출 (URL 끝의 숫자, 쿼리스트링 제외)
                # 예: https://blog.naver.com/980207/224179666791?fromRss=true
                clean_url = post["link"].split("?")[0]  # 쿼리스트링 제거
                match = re.search(r"/(\d+)$", clean_url)
                if match:
                    post["logNo"] = match.group(1)

            # 발행일
            pub_elem = item.find("pubDate")
            if pub_elem is not None and pub_elem.text:
                post["pubDate"] = pub_elem.text

            # 설명 (요약)
            desc_elem = item.find("description")
            if desc_elem is not None and desc_elem.text:
                # HTML 태그 제거
                desc = re.sub(r"<[^>]+>", "", desc_elem.text)
                desc = desc[:500] if len(desc) > 500 else desc
                post["description"] = desc

            posts.append(post)

            if limit and len(posts) >= limit:
                break

        return posts

    def get_post_content(self, log_no: str) -> Optional[dict]:
        """
        모바일 버전에서 포스트 본문 가져오기

        Args:
            log_no: 포스트 번호

        Returns:
            포스트 데이터 (제목, 본문, 이미지) 또는 None
        """
        url = f"https://m.blog.naver.com/{self.blog_id}/{log_no}"

        try:
            response = self.session.get(url, headers=self.MOBILE_HEADERS, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"포스트 요청 실패 ({log_no}): {e}")
            return None

        return self.parser.parse_mobile_post(response.text, self.blog_id, log_no)

    def scrape_all(self, limit: Optional[int] = None, include_content: bool = True, include_images: bool = False) -> list:
        """
        전체 스크래핑 (목록 + 본문)

        Args:
            limit: 스크래핑할 포스트 수
            include_content: 본문 포함 여부
            include_images: 이미지 URL 포함 여부

        Returns:
            전체 포스트 데이터 리스트
        """
        print(f"[1/2] 포스트 목록 가져오는 중...")
        posts = self.get_post_list(limit=limit)
        print(f"      {len(posts)}개 포스트 발견")

        if not include_content:
            return posts

        print(f"[2/2] 포스트 본문 가져오는 중...")
        results = []

        for i, post in enumerate(posts, 1):
            log_no = post.get("logNo")
            if not log_no:
                continue

            print(f"      [{i}/{len(posts)}] {post['title'][:30]}...")

            content_data = self.get_post_content(log_no)

            if content_data:
                # RSS 정보와 본문 정보 병합
                merged = {
                    **post,
                    "content": content_data.get("content", "")
                }
                if include_images:
                    merged["images"] = content_data.get("images", [])
                results.append(merged)
            else:
                results.append(post)

            # 딜레이
            if i < len(posts):
                time.sleep(self.delay)

        return results
