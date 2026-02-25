"""
YouTube 채널 스크래퍼 모듈
- YouTube Data API v3로 영상 목록 수집
- youtube-transcript-api로 자막 추출
"""

import json
import os
import re
import time
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 자막 추출 라이브러리
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    HAS_TRANSCRIPT_API = True
except ImportError:
    HAS_TRANSCRIPT_API = False


# 설정 파일 경로
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "keyword_config.json")


def load_api_key() -> str:
    """config/keyword_config.json에서 YouTube API 키 로드"""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get("YOUTUBE_API_KEY", "")
    except (FileNotFoundError, json.JSONDecodeError):
        return ""


class YouTubeScraper:
    """YouTube 채널 스크래퍼"""

    def __init__(self, channel_input: str, api_key: str = "", delay: float = 0.3):
        """
        Args:
            channel_input: 채널 ID, @handle, 또는 채널 URL
            api_key: YouTube Data API 키 (없으면 config에서 로드)
            delay: 요청 간 딜레이 (초)
        """
        self.api_key = api_key or load_api_key()
        if not self.api_key:
            raise ValueError("YouTube API 키가 없습니다. config/keyword_config.json을 확인하세요.")

        self.delay = delay
        self.youtube = build("youtube", "v3", developerKey=self.api_key)

        # 채널 ID 확인 (UC로 시작하는 정식 ID로 변환)
        self.channel_id = self._resolve_channel_id(channel_input)
        self.channel_info = None

    def _resolve_channel_id(self, input_str: str) -> str:
        """
        다양한 입력을 채널 ID로 변환

        지원 형식:
        - UC... (채널 ID 직접)
        - @handle
        - https://youtube.com/@handle
        - https://youtube.com/channel/UC...
        - 채널명 (검색)
        """
        input_str = input_str.strip()

        # 이미 채널 ID (UC로 시작)
        if input_str.startswith("UC") and len(input_str) == 24:
            return input_str

        # URL에서 추출
        if "youtube.com" in input_str or "youtu.be" in input_str:
            # @handle 형식
            handle_match = re.search(r"youtube\.com/@([^/?&]+)", input_str)
            if handle_match:
                input_str = f"@{handle_match.group(1)}"
            else:
                # /channel/UC... 형식
                channel_match = re.search(r"youtube\.com/channel/(UC[a-zA-Z0-9_-]{22})", input_str)
                if channel_match:
                    return channel_match.group(1)

        # @handle로 채널 검색
        if input_str.startswith("@"):
            handle = input_str[1:]  # @ 제거
            try:
                response = self.youtube.channels().list(
                    part="id,snippet",
                    forHandle=handle
                ).execute()

                if response.get("items"):
                    return response["items"][0]["id"]
            except HttpError:
                pass

        # 채널명으로 검색 (최후의 수단)
        try:
            response = self.youtube.search().list(
                part="snippet",
                q=input_str,
                type="channel",
                maxResults=1
            ).execute()

            if response.get("items"):
                return response["items"][0]["snippet"]["channelId"]
        except HttpError as e:
            print(f"채널 검색 실패: {e}")

        # 변환 실패 시 입력값 그대로 반환
        return input_str

    def get_channel_info(self) -> dict:
        """
        채널 기본 정보 가져오기

        Returns:
            채널 정보 (이름, 설명, 구독자수, 영상수, 썸네일)
        """
        try:
            response = self.youtube.channels().list(
                part="snippet,statistics,brandingSettings",
                id=self.channel_id
            ).execute()
        except HttpError as e:
            print(f"채널 정보 요청 실패: {e}")
            return {}

        if not response.get("items"):
            print(f"채널을 찾을 수 없습니다: {self.channel_id}")
            return {}

        item = response["items"][0]
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})

        self.channel_info = {
            "channel_id": self.channel_id,
            "channel_name": snippet.get("title", ""),
            "description": snippet.get("description", ""),
            "custom_url": snippet.get("customUrl", ""),
            "published_at": snippet.get("publishedAt", ""),
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
            "subscribers": int(stats.get("subscriberCount", 0)),
            "total_videos": int(stats.get("videoCount", 0)),
            "total_views": int(stats.get("viewCount", 0)),
            "channel_url": f"https://youtube.com/channel/{self.channel_id}"
        }

        return self.channel_info

    def get_video_list(self, limit: int = 10) -> list:
        """
        최신 영상 목록 가져오기

        Args:
            limit: 가져올 영상 수 (최대 50)

        Returns:
            영상 목록 (제목, ID, 날짜, 설명, 통계)
        """
        # 1단계: search.list로 영상 ID 목록 수집
        video_ids = []
        next_page_token = None
        remaining = min(limit, 50)

        while remaining > 0:
            try:
                max_results = min(remaining, 50)
                response = self.youtube.search().list(
                    part="id",
                    channelId=self.channel_id,
                    order="date",
                    type="video",
                    maxResults=max_results,
                    pageToken=next_page_token
                ).execute()
            except HttpError as e:
                print(f"영상 목록 요청 실패: {e}")
                break

            for item in response.get("items", []):
                video_ids.append(item["id"]["videoId"])
                remaining -= 1
                if remaining <= 0:
                    break

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

            time.sleep(self.delay)

        if not video_ids:
            return []

        # 2단계: videos.list로 상세 정보 한번에 가져오기 (50개씩)
        videos = []
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i + 50]
            try:
                response = self.youtube.videos().list(
                    part="snippet,statistics,contentDetails",
                    id=",".join(batch_ids)
                ).execute()
            except HttpError as e:
                print(f"영상 상세 정보 요청 실패: {e}")
                continue

            for item in response.get("items", []):
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})
                content = item.get("contentDetails", {})
                video_id = item["id"]

                # ISO 8601 duration → 읽기 쉬운 형식
                duration = self._parse_duration(content.get("duration", ""))

                # 기존 Post 호환 필드 + YouTube 전용 필드
                video = {
                    "title": snippet.get("title", ""),
                    "link": f"https://www.youtube.com/watch?v={video_id}",
                    "logNo": video_id,
                    "pubDate": snippet.get("publishedAt", ""),
                    "description": (snippet.get("description", "") or "")[:500],
                    "images": [
                        snippet.get("thumbnails", {}).get("high", {}).get("url", "")
                    ],
                    # YouTube 전용 필드
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "comments": int(stats.get("commentCount", 0)),
                    "tags": snippet.get("tags", []),
                    "duration": duration,
                    "category_id": snippet.get("categoryId", ""),
                }
                videos.append(video)

            if i + 50 < len(video_ids):
                time.sleep(self.delay)

        return videos

    def get_video_content(self, video_id: str) -> Optional[dict]:
        """
        영상 본문(자막) 가져오기

        Args:
            video_id: YouTube 영상 ID

        Returns:
            {"content": 자막 텍스트, "language": 언어코드} 또는 None
        """
        if not HAS_TRANSCRIPT_API:
            print("youtube-transcript-api가 설치되지 않았습니다.")
            return None

        ytt = YouTubeTranscriptApi()

        try:
            # 1순위: 한국어 자막 직접 요청
            try:
                result = ytt.fetch(video_id, languages=["ko"])
                text = "\n".join(snippet.text for snippet in result.snippets)
                return {"content": text, "language": result.language_code}
            except Exception:
                pass

            # 2순위: 영어 자막
            try:
                result = ytt.fetch(video_id, languages=["en"])
                text = "\n".join(snippet.text for snippet in result.snippets)
                return {"content": text, "language": result.language_code}
            except Exception:
                pass

            # 3순위: 사용 가능한 아무 자막
            try:
                transcript_list = ytt.list(video_id)
                for t in transcript_list:
                    result = ytt.fetch(video_id, languages=[t.language_code])
                    text = "\n".join(snippet.text for snippet in result.snippets)
                    return {"content": text, "language": result.language_code}
            except Exception:
                pass

        except Exception as e:
            print(f"      자막 없음 ({video_id}): {type(e).__name__}")

        return None

    def scrape_all(self, limit: int = 10, include_content: bool = True) -> list:
        """
        전체 스크래핑 (영상 목록 + 자막)

        Args:
            limit: 수집할 영상 수
            include_content: 자막 포함 여부

        Returns:
            전체 영상 데이터 리스트
        """
        # 채널 정보 가져오기
        print(f"[0/2] 채널 정보 가져오는 중...")
        channel_info = self.get_channel_info()
        if channel_info:
            print(f"      채널: {channel_info.get('channel_name', '?')} | 구독자: {channel_info.get('subscribers', 0):,}명")

        # 1단계: 영상 목록
        print(f"[1/2] 영상 목록 가져오는 중...")
        videos = self.get_video_list(limit=limit)
        print(f"      {len(videos)}개 영상 발견")

        if not include_content or not videos:
            return videos

        # 2단계: 자막 가져오기
        print(f"[2/2] 영상 자막 가져오는 중...")
        for i, video in enumerate(videos, 1):
            video_id = video.get("logNo")
            if not video_id:
                continue

            print(f"      [{i}/{len(videos)}] {video['title'][:30]}...")

            content_data = self.get_video_content(video_id)
            if content_data:
                video["content"] = content_data["content"]
                video["transcript_language"] = content_data["language"]
            else:
                # 자막 없으면 description을 content로 사용
                video["content"] = video.get("description", "")

            # 딜레이
            if i < len(videos):
                time.sleep(self.delay)

        return videos

    @staticmethod
    def _parse_duration(iso_duration: str) -> str:
        """
        ISO 8601 duration을 읽기 쉬운 형식으로 변환

        PT1H2M30S → 1:02:30
        PT15M4S → 15:04
        PT30S → 0:30
        """
        if not iso_duration:
            return ""

        match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso_duration)
        if not match:
            return iso_duration

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"

    def get_display_name(self) -> str:
        """출력용 채널 식별자 (yt_{handle 또는 channel_id})"""
        if self.channel_info and self.channel_info.get("custom_url"):
            # @handle에서 @ 제거
            handle = self.channel_info["custom_url"].lstrip("@")
            return f"yt_{handle}"
        return f"yt_{self.channel_id}"
