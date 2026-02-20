# 이달의 블로그 수집

인자: $ARGUMENTS

네이버 "이달의 블로그" 및 추천 블로그를 자동 수집합니다.

## 사용법 분기

**인자 분석:**
- 인자 없음 → 수집 실행 후 결과 표시
- `add` → 수집 후 선택한 블로그를 config/blogs.json에 추가
- `list` → 가장 최근 수집 결과만 표시

## 실행 방법

### 1. 수집 실행 (인자 없음)

Python 스크립트 실행:
```bash
cd "e:/Project/vibecode/Naver Scraping" && python scraper/monthly_blog.py
```

결과를 마크다운 표로 출력:
```
## 이달의 블로그 (N개 수집)

| # | ID | 제목/설명 |
|---|-----|-----------|
| 1 | blogId1 | 블로그 설명... |
| 2 | blogId2 | 블로그 설명... |

---
💡 `/monthly add` - 선택한 블로그 추가
💡 `/bloggers add <ID>` - 개별 추가
```

### 2. 블로그 추가 (`add`)

1. 먼저 수집 실행
2. 추가할 블로그 번호 입력 요청 (예: 1,3,5 또는 1-5)
3. 선택된 블로그를 `config/blogs.json`에 추가
4. 주제 자동 분류 제안

### 3. 최근 결과 보기 (`list`)

`output/monthly_blogs_*.json` 중 가장 최신 파일을 읽어서 표시.

## 참조 파일
- `scraper/monthly_blog.py`: Playwright 기반 수집 스크립트
- `output/monthly_blogs_*.json`: 수집 결과 저장
- `config/blogs.json`: 블로그 메타데이터
