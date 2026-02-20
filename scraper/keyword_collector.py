"""
네이버 블로그 기반 키워드 수집 모듈

네이버 검색 API를 활용하여:
- 키워드별 문서 수 조회
- 블로그 제목에서 연관 키워드 추출
- 자동완성 키워드 수집
- 경쟁도/최신성 분석
"""

import requests
import urllib.parse
import re
import json
import os
import time
from datetime import datetime, timedelta
from collections import Counter
from typing import List, Dict, Optional, Tuple

# 설정 파일 경로
CONFIG_FILE = "config/keyword_config.json"


def load_config() -> Dict:
    """설정 파일 로드"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}


def save_config(config: Dict):
    """설정 파일 저장"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


class KeywordCollector:
    """블로그 기반 키워드 수집기 (네이버 API 사용)"""

    # 불용어 (Stop words)
    STOP_WORDS = {
        '의', '가', '이', '은', '들', '는', '좀', '잘', '걍', '과', '도', '를', '으로', '자', '에', '와', '한', '하다',
        '및', '그', '저', '것', '수', '등', '더', '위', '중', '로', '만', '있다', '없다', '하는', '되는',
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        '있는', '없는', '하고', '되고', '된', '할', '될', '인', '적', '다음', '에서', '까지', '부터', '으로서'
    }

    # 검색 의도 패턴
    INTENT_PATTERNS = {
        "정보/프로필": ["프로필", "누구", "나이", "학력", "약력", "경력", "인물"],
        "후기/리뷰": ["후기", "리뷰", "솔직", "실제", "사용", "체험", "방문"],
        "방법/가이드": ["방법", "하는법", "만들기", "설치", "사용법", "가이드", "팁"],
        "추천/비교": ["추천", "비교", "순위", "best", "top", "베스트", "인기"],
        "뉴스/이슈": ["라며", "사건", "뉴스", "속보", "발표", "결정", "판결"],
        "가격/비용": ["가격", "비용", "얼마", "할인", "세일", "무료", "유료"],
        "여행/맛집": ["맛집", "여행", "코스", "일정", "예약", "관광", "포인"],
        "감상/분석": ["줄거리", "결말", "해석", "분석", "정리", "요약", "스포"]
    }

    def __init__(self, client_id: str = None, client_secret: str = None):
        """
        Args:
            client_id: 네이버 검색 API Client ID
            client_secret: 네이버 검색 API Client Secret
        """
        # 설정 파일에서 로드
        if client_id is None or client_secret is None:
            config = load_config()
            client_id = client_id or config.get("NAVER_BLOG_CLIENT_ID", "")
            client_secret = client_secret or config.get("NAVER_BLOG_CLIENT_SECRET", "")

        self.client_id = client_id
        self.client_secret = client_secret
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def _get_api_headers(self) -> dict:
        """API 요청 헤더 생성"""
        return {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }

    def is_configured(self) -> bool:
        """API 키가 설정되어 있는지 확인"""
        return bool(self.client_id and self.client_secret)

    def get_document_count(self, keyword: str) -> int:
        """
        키워드의 블로그 문서 수 조회

        Args:
            keyword: 검색할 키워드

        Returns:
            블로그 문서 총 개수
        """
        if not self.is_configured():
            print("[오류] API 키가 설정되지 않았습니다.")
            return 0

        try:
            enc_text = urllib.parse.quote(keyword)
            url = f"https://openapi.naver.com/v1/search/blog?query={enc_text}&display=1"

            response = requests.get(url, headers=self._get_api_headers(), timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get("total", 0)
        except Exception as e:
            print(f"[오류] 문서 수 조회 실패 ({keyword}): {e}")
            return 0

    def get_blog_titles(self, keyword: str, display: int = 50) -> List[Dict]:
        """
        블로그 검색 결과에서 제목과 메타 정보 가져오기

        Args:
            keyword: 검색할 키워드
            display: 가져올 결과 수 (최대 100)

        Returns:
            [{"title": "...", "blogger": "...", "date": "...", "link": "..."}, ...]
        """
        if not self.is_configured():
            return []

        try:
            enc_text = urllib.parse.quote(keyword)
            url = f"https://openapi.naver.com/v1/search/blog?query={enc_text}&display={display}&sort=sim"

            response = requests.get(url, headers=self._get_api_headers(), timeout=10)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("items", []):
                title = item.get("title", "").replace("<b>", "").replace("</b>", "")
                results.append({
                    "title": title,
                    "blogger": item.get("bloggername", ""),
                    "date": item.get("postdate", ""),
                    "link": item.get("link", ""),
                    "description": item.get("description", "").replace("<b>", "").replace("</b>", "")
                })
            return results
        except Exception as e:
            print(f"[오류] 블로그 제목 조회 실패 ({keyword}): {e}")
            return []

    def get_autocomplete_keywords(self, keyword: str, limit: int = 10) -> List[str]:
        """
        네이버 자동완성에서 연관 키워드 가져오기 (API 키 불필요)

        Args:
            keyword: 기본 키워드
            limit: 최대 결과 수

        Returns:
            자동완성 키워드 리스트
        """
        try:
            enc_text = urllib.parse.quote(keyword)
            url = f"https://ac.search.naver.com/nx/ac?q={enc_text}&con=1&frm=nv&ans=2&r_format=json&r_enc=UTF-8&r_unicode=0&t_koreng=1&run=2&rev=4&q_enc=UTF-8"

            response = requests.get(url, headers=self.headers, timeout=5)
            response.raise_for_status()
            data = response.json()

            suggestions = []
            items = data.get("items", [])
            if items and len(items) > 0:
                for item in items[0]:
                    if isinstance(item, list) and len(item) > 0:
                        suggestions.append(item[0])

            return suggestions[:limit]
        except Exception as e:
            print(f"[오류] 자동완성 조회 실패 ({keyword}): {e}")
            return []

    def extract_keywords_from_titles(self, base_keyword: str, titles: List[Dict]) -> List[str]:
        """
        블로그 제목에서 연관 키워드 추출

        Args:
            base_keyword: 기본 키워드
            titles: get_blog_titles() 결과

        Returns:
            "기본키워드 + 추출단어" 조합 리스트
        """
        base_words = set(re.split(r'[,\s·|:\-\[\]()]+', base_keyword.lower()))
        base_words = {w.strip() for w in base_words if len(w.strip()) >= 2}

        word_counter = Counter()

        for item in titles:
            title = item.get("title", "")
            title_clean = title.replace(base_keyword, '')
            words = re.split(r'[,\s·|:\-\[\]()「」『』【】]+', title_clean)

            for word in words:
                word = word.strip()
                if len(word) >= 2 and word not in self.STOP_WORDS and word.lower() not in base_words:
                    word_counter[word] += 1

        extracted = []
        for word, count in word_counter.most_common(30):
            if count >= 2 and len(extracted) < 15:
                combined = f"{base_keyword} {word}"
                extracted.append(combined)

        return extracted

    def get_recent_blog_count(self, keyword: str, days: int = 30) -> int:
        """
        최근 N일간 발행된 블로그 글 수 조회 (경쟁도 판단용)

        Args:
            keyword: 검색할 키워드
            days: 최근 며칠간

        Returns:
            최근 발행된 블로그 글 수
        """
        if not self.is_configured():
            return 0

        try:
            enc_text = urllib.parse.quote(keyword)
            url = f"https://openapi.naver.com/v1/search/blog?query={enc_text}&display=100&sort=date"

            response = requests.get(url, headers=self._get_api_headers(), timeout=10)
            response.raise_for_status()
            data = response.json()

            cutoff_date = datetime.now() - timedelta(days=days)
            recent_count = 0

            for item in data.get("items", []):
                postdate = item.get("postdate", "")
                if postdate and len(postdate) == 8:
                    try:
                        post_dt = datetime.strptime(postdate, "%Y%m%d")
                        if post_dt >= cutoff_date:
                            recent_count += 1
                    except:
                        pass

            return recent_count
        except Exception as e:
            print(f"[오류] 최근 블로그 수 조회 실패 ({keyword}): {e}")
            return 0

    def get_news_count(self, keyword: str, days: int = 7) -> Dict:
        """
        최근 N일간 뉴스 기사 수 조회 (최신성 확인)

        Args:
            keyword: 검색할 키워드
            days: 최근 며칠간

        Returns:
            {"total": 전체수, "recent": 최근수}
        """
        if not self.is_configured():
            return {"total": 0, "recent": 0}

        try:
            enc_text = urllib.parse.quote(keyword)
            url = f"https://openapi.naver.com/v1/search/news?query={enc_text}&display=100&sort=date"

            response = requests.get(url, headers=self._get_api_headers(), timeout=10)
            response.raise_for_status()
            data = response.json()

            total = data.get("total", 0)
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_news = 0

            for item in data.get("items", []):
                pubdate = item.get("pubDate", "")
                if pubdate:
                    try:
                        from email.utils import parsedate_to_datetime
                        pub_dt = parsedate_to_datetime(pubdate)
                        pub_dt = pub_dt.replace(tzinfo=None)
                        if pub_dt >= cutoff_date:
                            recent_news += 1
                    except:
                        pass

            return {"total": total, "recent": recent_news}
        except Exception as e:
            print(f"[오류] 뉴스 수 조회 실패 ({keyword}): {e}")
            return {"total": 0, "recent": 0}

    def analyze_search_intent(self, keyword: str, titles: List[Dict]) -> List[Tuple[str, int]]:
        """
        블로그 제목에서 검색 의도 분석

        Args:
            keyword: 기본 키워드
            titles: get_blog_titles() 결과

        Returns:
            [(의도, 횟수), ...] 상위 3개
        """
        title_text = ' '.join([t.get("title", "") for t in titles]).lower()

        intent_counts = {k: 0 for k in self.INTENT_PATTERNS.keys()}

        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if pattern in title_text:
                    intent_counts[intent] += title_text.count(pattern)

        sorted_intents = sorted(intent_counts.items(), key=lambda x: x[1], reverse=True)
        return [(k, v) for k, v in sorted_intents if v > 0][:3]

    def analyze_keyword(self, keyword: str, analyze_competition: bool = True,
                       analyze_recency: bool = True, analyze_intent: bool = True) -> Dict:
        """
        키워드 종합 분석

        Args:
            keyword: 분석할 키워드
            analyze_competition: 경쟁도 분석 여부
            analyze_recency: 최신성 분석 여부
            analyze_intent: 검색 의도 분석 여부

        Returns:
            종합 분석 결과
        """
        result = {
            "keyword": keyword,
            "docs": 0,
            "is_golden": False,
            "rating": "",
            "competition": {},
            "recency": {},
            "intent": [],
            "related_keywords": []
        }

        # 문서 수 조회
        result["docs"] = self.get_document_count(keyword)
        time.sleep(0.1)

        # 골든 키워드 판별
        docs = result["docs"]
        if docs < 5000:
            result["is_golden"] = True
            result["rating"] = "⭐⭐⭐ 매우 좋음 (저경쟁 블루오션)"
        elif docs < 10000:
            result["is_golden"] = True
            result["rating"] = "⭐⭐ 좋음 (진입 용이)"
        elif docs < 20000:
            result["rating"] = "⭐ 보통 (적정 경쟁)"
        else:
            result["rating"] = "경쟁 있음 (레드오션)"

        # 블로그 제목 수집 (연관 키워드 및 의도 분석용)
        titles = self.get_blog_titles(keyword, display=50)
        time.sleep(0.1)

        # 경쟁도 분석
        if analyze_competition:
            recent_blogs = self.get_recent_blog_count(keyword, days=30)
            if recent_blogs < 10:
                comp_rating = "🟢 매우 낮음 (바로 진입!)"
            elif recent_blogs < 30:
                comp_rating = "🟡 낮음 (진입 가능)"
            elif recent_blogs < 50:
                comp_rating = "🟠 보통 (세부 키워드 고려)"
            else:
                comp_rating = "🔴 높음 (세부 키워드 필요)"

            result["competition"] = {
                "recent_30days": recent_blogs,
                "rating": comp_rating
            }
            time.sleep(0.1)

        # 최신성 분석
        if analyze_recency:
            news_data = self.get_news_count(keyword, days=7)
            if news_data["recent"] > 10:
                news_rating = "🔥 핫이슈 (신속히 작성!)"
            elif news_data["recent"] > 5:
                news_rating = "📰 이슈 있음 (빠르게 작성)"
            elif news_data["recent"] > 0:
                news_rating = "📝 약간의 뉴스 (심층 분석글)"
            else:
                news_rating = "📄 이슈 없음 (심층 분석글 추천)"

            result["recency"] = {
                "news_total": news_data["total"],
                "news_recent_7days": news_data["recent"],
                "rating": news_rating
            }
            time.sleep(0.1)

        # 검색 의도 분석
        if analyze_intent and titles:
            result["intent"] = self.analyze_search_intent(keyword, titles)

        # 연관 키워드 추출
        if titles:
            extracted = self.extract_keywords_from_titles(keyword, titles)
            autocomplete = self.get_autocomplete_keywords(keyword)

            all_related = []
            seen = set()
            for kw in extracted + autocomplete:
                if kw.lower() not in seen:
                    seen.add(kw.lower())
                    all_related.append(kw)

            result["related_keywords"] = all_related[:20]

        return result

    def collect_keywords(self, seed_keywords: List[str], max_keywords: int = 100,
                        golden_threshold: int = 10000) -> List[Dict]:
        """
        시드 키워드에서 연관 키워드까지 수집

        Args:
            seed_keywords: 시작 키워드 리스트
            max_keywords: 최대 수집할 키워드 수
            golden_threshold: 골든 키워드 기준 문서 수

        Returns:
            수집된 키워드 분석 결과 리스트
        """
        all_keywords = list(seed_keywords)
        searched = set()
        results = []

        print(f"[키워드 수집] 시드 키워드 {len(seed_keywords)}개에서 시작...")

        for seed in seed_keywords:
            if seed in searched:
                continue
            searched.add(seed)

            print(f"  → '{seed}' 연관 키워드 추출 중...")

            titles = self.get_blog_titles(seed, display=50)
            if titles:
                extracted = self.extract_keywords_from_titles(seed, titles)
                for kw in extracted:
                    if kw not in all_keywords:
                        all_keywords.append(kw)

            autocomplete = self.get_autocomplete_keywords(seed)
            for kw in autocomplete:
                if kw not in all_keywords:
                    all_keywords.append(kw)

            time.sleep(0.2)

        print(f"[키워드 수집] 총 {len(all_keywords)}개 키워드 발견, 분석 시작...")

        for i, keyword in enumerate(all_keywords[:max_keywords]):
            if keyword in searched and keyword not in seed_keywords:
                continue

            print(f"  [{i+1}/{min(len(all_keywords), max_keywords)}] '{keyword}' 분석 중...")

            docs = self.get_document_count(keyword)

            is_golden = docs <= golden_threshold
            if docs < 5000:
                rating = "⭐⭐⭐ 매우 좋음"
            elif docs < 10000:
                rating = "⭐⭐ 좋음"
            elif docs < 20000:
                rating = "⭐ 보통"
            else:
                rating = "경쟁 있음"

            results.append({
                "keyword": keyword,
                "docs": docs,
                "is_golden": is_golden,
                "rating": rating
            })

            time.sleep(0.1)

        results.sort(key=lambda x: x["docs"])

        golden_count = sum(1 for r in results if r["is_golden"])
        print(f"\n[완료] 총 {len(results)}개 키워드 분석, 골든 키워드 {golden_count}개")

        return results


def save_results(results: List[Dict], keyword: str, output_dir: str = "output"):
    """결과를 JSON 파일로 저장"""
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_keyword = re.sub(r'[<>:"/\\|?*]', '', keyword).strip()[:20]
    filename = f"{output_dir}/keywords_{safe_keyword}_{timestamp}.json"

    output = {
        "seed_keyword": keyword,
        "collected_at": datetime.now().isoformat(),
        "total_keywords": len(results),
        "golden_count": sum(1 for r in results if r.get("is_golden")),
        "keywords": results
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"[저장 완료] {filename}")
    return filename


# CLI 실행
if __name__ == "__main__":
    import sys

    config = load_config()
    collector = KeywordCollector()

    if not collector.is_configured():
        print("=" * 50)
        print("네이버 검색 API 키가 필요합니다.")
        print("=" * 50)
        print("\n1. https://developers.naver.com 에서 애플리케이션 등록")
        print("2. 검색 API 사용 신청")
        print("3. Client ID와 Client Secret 발급")
        print("\n아래 정보를 입력하세요:")

        client_id = input("Client ID: ").strip()
        client_secret = input("Client Secret: ").strip()

        if client_id and client_secret:
            config["NAVER_BLOG_CLIENT_ID"] = client_id
            config["NAVER_BLOG_CLIENT_SECRET"] = client_secret
            save_config(config)
            collector = KeywordCollector(client_id, client_secret)
            print("\n[저장 완료] API 키가 저장되었습니다.")
        else:
            print("[오류] API 키를 입력해주세요.")
            sys.exit(1)

    print("\n" + "=" * 50)
    print("블로그 키워드 수집기 (네이버 API)")
    print("=" * 50)

    keyword = input("\n분석할 키워드 (쉼표로 구분): ").strip()
    if not keyword:
        print("[오류] 키워드를 입력해주세요.")
        sys.exit(1)

    keywords = [k.strip() for k in keyword.split(",") if k.strip()]

    max_count = input("최대 수집 키워드 수 [기본: 50]: ").strip()
    max_count = int(max_count) if max_count.isdigit() else 50

    results = collector.collect_keywords(keywords, max_keywords=max_count)

    print("\n" + "=" * 50)
    print("골든 키워드 TOP 10")
    print("=" * 50)

    golden = [r for r in results if r["is_golden"]][:10]
    for i, r in enumerate(golden, 1):
        print(f"{i}. {r['keyword']} - 문서 {r['docs']:,}개 {r['rating']}")

    save_results(results, keywords[0])
