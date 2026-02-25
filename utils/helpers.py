"""
유틸리티 함수 모듈
"""

import json
import os
from datetime import datetime


def save_json(data: list | dict, filepath: str) -> str:
    """
    데이터를 JSON 파일로 저장

    Args:
        data: 저장할 데이터
        filepath: 저장 경로

    Returns:
        저장된 파일 경로
    """
    # 디렉토리 생성
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filepath


def save_posts_to_files(posts: list, output_dir: str = "output", prefix: str = "") -> dict:
    """
    포스트 데이터를 파일로 저장

    Args:
        posts: 포스트 리스트
        output_dir: 출력 디렉토리
        prefix: 파일명 앞에 붙일 접두사 (예: 블로그 ID)

    Returns:
        저장 결과 정보
    """
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 파일명 생성 (prefix가 있으면 prefix_summary_날짜.json)
    if prefix:
        posts_filename = f"{prefix}_posts_{timestamp}.json"
        summary_filename = f"{prefix}_summary_{timestamp}.json"
    else:
        posts_filename = f"posts_{timestamp}.json"
        summary_filename = f"summary_{timestamp}.json"

    # 전체 데이터 저장
    all_posts_file = os.path.join(output_dir, posts_filename)
    save_json(posts, all_posts_file)

    # 요약 정보 저장
    def parse_pubdate(pub_date_str):
        """pubDate에서 요일 추출"""
        if not pub_date_str:
            return ""
        # "Tue, 27 Jan 2026 08:02:27 +0900" 형식
        day_map = {"Mon": "월", "Tue": "화", "Wed": "수", "Thu": "목", "Fri": "금", "Sat": "토", "Sun": "일"}
        parts = pub_date_str.split(",")
        if parts:
            day_abbr = parts[0].strip()
            return day_map.get(day_abbr, day_abbr)
        return ""

    def build_post_summary(i, p):
        title = p.get("title", "")
        content = p.get("content", "")
        pub_date = p.get("pubDate", "")
        log_no = p.get("logNo", "")
        images = p.get("images", [])

        return {
            "index": f"{i:02d}",
            "logNo": log_no,
            "url": f"https://blog.naver.com/{prefix}/{log_no}" if prefix and log_no else "",
            "title": title,
            "title_length": len(title),
            "pubDate": pub_date,
            "day_of_week": parse_pubdate(pub_date),
            "has_content": bool(content),
            "content_length": len(content) if content else 0,
            "image_count": len(images)
        }

    summary = {
        "_guide": {
            "출력규칙": "반드시 마크다운 표(|---|---|) 형식 사용. 각 섹션은 ### 헤더로 구분. 항목별 상세 설명 필수.",
            "전체분석": {
                "설명": "블로그 전체를 12가지 항목으로 종합 분석",
                "형식": "각 항목마다 마크다운 표(항목|점수/100|분석내용) 사용",
                "항목": ["콘텐츠장단점", "운영자문제점", "SEO개선점", "전략제안", "타겟독자", "브랜딩", "발행패턴", "제목패턴", "수익화", "경쟁환경", "AI대응력", "독자참여도"],
                "필수": "각 항목 100점 만점 점수 + 장점/단점/개선안 구체적 서술"
            },
            "특정글분석": {
                "설명": "posts 파일에서 index 번호로 지정된 글의 본문을 심층 분석",
                "형식": [
                    "### 1. 콘텐츠 구조 분석 - 마크다운 표(구성요소|내용|평가) + 별점(★) 5점 만점",
                    "### 2. 강점 4가지 - 번호 매기고 각각 2-3문장으로 상세 설명",
                    "### 3. 약점 및 개선점 - 마크다운 표(약점|현재상태|개선방안) 3개 이상",
                    "### 4. SEO 분석 - 제목패턴, 핵심키워드 5개, 추천 메타설명 50자 이상",
                    "### 5. 독자 반응 예측 - 마크다운 표(반응유형|예상반응|근거) 4개 이상",
                    "### 6. 종합 평가 - 마크다운 표(평가항목|점수/100|코멘트) 정보성,가독성,SEO,독창성,실용성",
                    "### 7. 총평 - 3-4문장으로 글의 가치와 개선 방향 요약"
                ]
            },
            "빠른요약": {
                "설명": "블로그 전체를 3줄로 요약",
                "형식": ["- **주제**: ...", "- **강점**: ...", "- **개선점**: ..."]
            },
            "제목분석": {
                "설명": "제목 패턴과 SEO 분석",
                "형식": ["제목패턴 분류표", "SEO 키워드 추출", "개선 필요 제목 3개 + 수정안"]
            }
        },
        "blog_id": prefix,
        "blog_url": f"https://blog.naver.com/{prefix}" if prefix else "",
        "total_posts": len(posts),
        "scraped_at": datetime.now().isoformat(),
        "posts": [build_post_summary(i, p) for i, p in enumerate(posts)]
    }

    summary_file = os.path.join(output_dir, summary_filename)
    save_json(summary, summary_file)

    return {
        "posts_file": all_posts_file,
        "summary_file": summary_file,
        "total": len(posts)
    }


def save_youtube_to_files(videos: list, channel_info: dict, output_dir: str = "output", prefix: str = "") -> dict:
    """
    YouTube 영상 데이터를 파일로 저장

    Args:
        videos: 영상 리스트
        channel_info: 채널 정보 딕셔너리
        output_dir: 출력 디렉토리
        prefix: 파일명 접두사 (예: yt_techmong)

    Returns:
        저장 결과 정보
    """
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if prefix:
        posts_filename = f"{prefix}_posts_{timestamp}.json"
        summary_filename = f"{prefix}_summary_{timestamp}.json"
    else:
        posts_filename = f"posts_{timestamp}.json"
        summary_filename = f"summary_{timestamp}.json"

    # 전체 데이터 저장
    all_posts_file = os.path.join(output_dir, posts_filename)
    save_json(videos, all_posts_file)

    # 요약 정보 저장
    def parse_pubdate_yt(pub_date_str):
        """YouTube publishedAt에서 요일 추출 (ISO 8601)"""
        if not pub_date_str:
            return ""
        try:
            dt = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
            day_map = {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"}
            return day_map.get(dt.weekday(), "")
        except (ValueError, AttributeError):
            return ""

    def format_number(n):
        """숫자를 읽기 쉬운 형식으로"""
        if n >= 10000:
            return f"{n / 10000:.1f}만"
        elif n >= 1000:
            return f"{n / 1000:.1f}천"
        return str(n)

    def build_video_summary(i, v):
        title = v.get("title", "")
        content = v.get("content", "")
        pub_date = v.get("pubDate", "")
        video_id = v.get("logNo", "")
        images = v.get("images", [])

        return {
            "index": f"{i:02d}",
            "logNo": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}" if video_id else "",
            "title": title,
            "title_length": len(title),
            "pubDate": pub_date,
            "day_of_week": parse_pubdate_yt(pub_date),
            "has_content": bool(content),
            "content_length": len(content) if content else 0,
            "image_count": len(images),
            # YouTube 전용
            "views": v.get("views", 0),
            "likes": v.get("likes", 0),
            "comments": v.get("comments", 0),
            "duration": v.get("duration", ""),
        }

    summary = {
        "_guide": {
            "출력규칙": "반드시 마크다운 표(|---|---|) 형식 사용. 각 섹션은 ### 헤더로 구분. 항목별 상세 설명 필수.",
            "플랫폼": "youtube",
            "전체분석": {
                "설명": "YouTube 채널 전체를 종합 분석",
                "형식": "각 항목마다 마크다운 표(항목|점수/100|분석내용) 사용",
                "항목": ["콘텐츠장단점", "운영자문제점", "SEO개선점", "전략제안", "타겟독자", "브랜딩", "발행패턴", "제목패턴", "수익화", "경쟁환경", "AI대응력", "독자참여도"],
                "필수": "각 항목 100점 만점 점수 + 장점/단점/개선안 구체적 서술"
            },
            "youtube분석": {
                "설명": "YouTube 채널 전용 분석 (전체분석에 추가)",
                "항목": [
                    "주요 제품군/주제 TOP 5 (비율 포함)",
                    "조회수 높은 주제 패턴 (평균 조회수 기준 랭킹)",
                    "업로드 빈도, 요일, 시간대",
                    "영상 길이 분포 (숏폼/미들/롱폼)",
                    "제목 패턴 (낚시성, 키워드, 이모지 사용)",
                    "협찬/광고 비율 추정",
                    "태그 활용도",
                    "구독자 대비 조회율"
                ]
            },
            "특정글분석": {
                "설명": "posts 파일에서 index 번호로 지정된 영상의 자막(content)을 심층 분석",
                "형식": [
                    "### 1. 콘텐츠 구조 분석 - 마크다운 표(구성요소|내용|평가) + 별점(★) 5점 만점",
                    "### 2. 강점 4가지 - 번호 매기고 각각 2-3문장으로 상세 설명",
                    "### 3. 약점 및 개선점 - 마크다운 표(약점|현재상태|개선방안) 3개 이상",
                    "### 4. SEO 분석 - 제목패턴, 핵심키워드 5개, 추천 메타설명 50자 이상",
                    "### 5. 시청자 반응 예측 - 마크다운 표(반응유형|예상반응|근거) 4개 이상",
                    "### 6. 종합 평가 - 마크다운 표(평가항목|점수/100|코멘트) 정보성,가독성,SEO,독창성,실용성",
                    "### 7. 총평 - 3-4문장으로 영상의 가치와 개선 방향 요약"
                ]
            },
            "빠른요약": {
                "설명": "채널 전체를 3줄로 요약",
                "형식": ["- **주제**: ...", "- **강점**: ...", "- **개선점**: ..."]
            }
        },
        "platform": "youtube",
        "blog_id": prefix,
        "channel_id": channel_info.get("channel_id", ""),
        "channel_name": channel_info.get("channel_name", ""),
        "channel_url": channel_info.get("channel_url", ""),
        "subscribers": channel_info.get("subscribers", 0),
        "subscribers_display": format_number(channel_info.get("subscribers", 0)),
        "total_videos": channel_info.get("total_videos", 0),
        "total_views": channel_info.get("total_views", 0),
        "blog_url": channel_info.get("channel_url", ""),
        "total_posts": len(videos),
        "scraped_at": datetime.now().isoformat(),
        "posts": [build_video_summary(i, v) for i, v in enumerate(videos)]
    }

    summary_file = os.path.join(output_dir, summary_filename)
    save_json(summary, summary_file)

    return {
        "posts_file": all_posts_file,
        "summary_file": summary_file,
        "total": len(videos)
    }
