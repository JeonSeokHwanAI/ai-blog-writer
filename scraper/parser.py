"""
HTML 파싱 모듈
- 모바일 버전 포스트 본문 파싱
"""

import re
from bs4 import BeautifulSoup


class PostParser:
    """네이버 블로그 포스트 HTML 파서"""

    @staticmethod
    def parse_mobile_post(html: str, blog_id: str, log_no: str) -> dict:
        """
        모바일 버전 포스트 HTML 파싱

        Args:
            html: HTML 문자열
            blog_id: 블로그 ID
            log_no: 포스트 번호

        Returns:
            파싱된 포스트 데이터 딕셔너리
        """
        soup = BeautifulSoup(html, "html.parser")

        result = {
            "blogId": blog_id,
            "logNo": log_no,
            "title": "",
            "content": "",
            "images": []
        }

        # 제목 추출
        result["title"] = PostParser._extract_title(soup)

        # 본문 추출
        result["content"] = PostParser._extract_content(soup)

        # 이미지 추출
        result["images"] = PostParser._extract_images(soup)

        return result

    @staticmethod
    def _extract_title(soup: BeautifulSoup) -> str:
        """제목 추출"""
        title_elem = soup.find("title")
        if title_elem:
            title = title_elem.get_text(strip=True)
            # " : 네이버 블로그" 제거
            title = re.sub(r"\s*:\s*네이버\s*블로그.*$", "", title)
            return title
        return ""

    @staticmethod
    def _extract_content(soup: BeautifulSoup) -> str:
        """본문 추출"""
        # 여러 선택자 시도
        content_selectors = [
            {"class_": "se-main-container"},
            {"class_": "post_ct"},
            {"id": "postViewArea"},
            {"class_": "__se_component_area"}
        ]

        content_text = ""
        for selector in content_selectors:
            content_elem = soup.find("div", **selector)
            if content_elem:
                content_text = content_elem.get_text(separator="\n", strip=True)
                break

        # 대안: se-text 클래스들 수집
        if not content_text:
            text_elems = soup.find_all(class_=re.compile(r"se-text|se_textarea"))
            if text_elems:
                texts = [e.get_text(strip=True) for e in text_elems]
                content_text = "\n".join(texts)

        # 특수 문자 제거 (zero-width space 등)
        content_text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', content_text)

        return content_text

    @staticmethod
    def _extract_images(soup: BeautifulSoup) -> list:
        """이미지 URL 추출"""
        images = []
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src")
            if src and ("blogthumb" in src or "postfiles" in src or "pstatic" in src):
                # 썸네일이 아닌 원본 이미지 URL로 변환
                if "type=w80" in src:
                    src = re.sub(r"\?type=w\d+.*$", "", src)
                images.append(src)
        return images
