# AI Blog Writer

> AI는 펜이고, 당신이 작가입니다.

AI 블로그 작가가 만든 네이버 블로그/유튜브 스크래핑, 분석, 글쓰기 플랫폼입니다.
블로그 분석부터 페르소나 기반 글쓰기까지, AI를 파트너로 활용하여 나만의 블로그 작가가 되는 도구입니다.

## 프로젝트 구조

```
├── main.py                      # 메인 스크래퍼 실행
├── config/                      # 설정 및 상태 파일
│   ├── blogs.json               # 블로그 목록
│   ├── personas/                # 페르소나별 JSON 파일
│   │   └── AI블로그작가.json
│   ├── .active_persona.json     # 현재 활성 페르소나 (숨김)
│   ├── naver_topics.json        # 네이버 주제 카테고리
│   └── keyword_config.json      # 키워드 API 설정
├── scraper/                     # 스크래핑 모듈
│   ├── blog_scraper.py          # 블로그 포스트 수집
│   ├── youtube_scraper.py       # YouTube 채널 수집
│   └── monthly_blog.py          # 이달의 블로그 수집
├── utils/                       # 유틸리티 함수
├── output/                      # 스크래핑 결과
│   └── {blog_id}/               # 각 블로그 ID별 폴더
├── docs/                        # 문서
│   ├── blog/                    # 블로그 글 작성 (초안)
│   ├── clips/                   # 클리핑된 블로그 글
│   ├── reviews/                 # 블로그 리뷰 저장
│   └── context/                 # 글쓰기 참조 파일 (페르소나 등)
└── .claude/commands/            # 슬래시 명령어
```

## Commands (슬래시 명령어)

### 수집 및 분석

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `/search` | 블로그/유튜브 스크래핑 | `/search zeroenter 5`, `/search yt:@techmong 10` |
| `/review` | 블로그 분석 리뷰 | `/review 비움 00`, `/review 비움 0` (전체분석) |
| `/keyword` | 키워드 분석 | `/keyword AI 바이브 코딩` |
| `/monthly` | 이달의 블로그 수집 | `/monthly add` |

### 블로거 관리

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `/bloggers` | 블로거 목록 관리 | `/bloggers *` (즐겨찾기) |
| `/bloggers add` | 새 블로그 추가 | `/bloggers add zeroenter` |

### 콘텐츠 생성

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `/persona` | 페르소나 관리 | `/persona list`, `/persona use AI블로그작가` |
| `/write` | 블로그 글 작성 | `/write` 또는 `/write 제목` |

### 저장

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `/save` | 블로그 리뷰 저장 | `/save` |
| `/clip` | 블로그 글 클리핑 | `/clip list` |

---

## 사전 준비 (처음 사용 시)

### 방법 1: 자동 설치 (권장)

| OS | 파일 | 실행 방법 |
|----|------|-----------|
| Windows | `setup.bat` | 더블클릭 |
| Mac/Linux | `setup.sh` | 터미널에서 `bash setup.sh` |

- Python 없으면 → 자동 설치 (Windows: winget, Mac: Homebrew)
- pip 업그레이드
- 필수 패키지 설치
- Playwright 설치 (선택)

> Windows 자동 설치 실패 시: `setup.bat` 우클릭 → "관리자 권한으로 실행"

### 방법 2: 수동 설치

1. **Python 설치**: https://www.python.org/downloads/
   - 설치 시 "Add Python to PATH" 반드시 체크!

2. **패키지 설치**:
```bash
pip install -r requirements.txt
```

3. **Playwright 설치** (이달의 블로그 기능 사용 시):
```bash
playwright install chromium
```

### 방법 3: Claude Code에서 `/setup`

```
/setup          # 환경 점검 + 자동 설치
/setup check    # 점검만 (설치 안 함)
```

---

## 상세 사용법

### /search {blog_id} {count}
블로그/유튜브 스크래퍼 실행. 별명/블로그명 자동 매칭 지원.

**네이버 블로그:**
```
/search 980207        # 최신 1개 포스트
/search zeroenter 5   # 5개 포스트
/search 리리 3        # 별명 매칭 → ari_school
```

**YouTube** (`yt:` 접두사):
```
/search yt:@techmong      # 테크몽 채널 최신 1개
/search yt:@techmong 10   # 최신 10개
/search yt:테크몽 5       # 채널명 검색 → 5개
```

> YouTube 기능은 YouTube Data API 키가 필요합니다. `config/keyword_config.json`에 `YOUTUBE_API_KEY`를 설정하세요.

### /review {별명/ID} {포스트번호|0}
수집된 데이터로 블로그 분석. 직전 `/search` 결과를 자동 연결.

```
/review                # 직전 search 결과 자동 분석
/review 비움 00        # hhey0510의 00번 포스트 분석
/review 비움 0         # hhey0510 전체분석 (12개 항목)
/review 리리 댓글      # 최신 글 댓글만 바로 출력
```

- **전체분석 (0)**: 12개 항목 (콘텐츠장단점, 운영자문제점, SEO개선점, 전략제안 등)
- **특정글분석**: 8개 섹션 (구조분석, 강점, 약점, SEO, 독자반응, 종합평가, 총평, 추천댓글)

### /keyword {키워드}
WebSearch로 키워드 분석: 연관 키워드, 검색 의도, 콘텐츠 추천.

### /monthly
네이버 "이달의 블로그" 자동 수집.
- `/monthly` - 수집 실행
- `/monthly add` - 수집 후 blogs.json에 추가

### /bloggers
블로그 목록 관리.
- `*` - 즐겨찾기만 보기
- `#주제` - 주제 필터링
- `@ID` - ID로 검색
- `+ID` / `-ID` - 즐겨찾기 추가/제거

### /persona
페르소나 관리 (생성/전환/수정). 여러 명의 블로그 스타일을 등록하고 전환 가능.
- `/persona` - 현재 활성 페르소나 표시
- `/persona list` - 등록된 페르소나 목록
- `/persona create <이름>` - 새 페르소나 직접 생성 (인터뷰)
- `/persona <블로그ID>` - 블로그 분석 → 페르소나 자동 생성
- `/persona use <이름>` - 페르소나 전환 (빙의)

### /write {제목}
블로그 글 작성 (단계별 진행).
1. 이전 `/keyword` 결과 활용 여부 확인
2. 추가 내용 입력 → **작성자 원본** 저장
3. **본문** 초안 작성
4. "완성할까요?" → 예 선택 시 제목/이미지/태그 생성

### /save
분석한 블로그 글을 `docs/reviews/`에 저장.

### /clip
읽은 블로그 글을 `docs/clips/`에 클리핑.

---

## 파일 저장 위치

| 파일 유형 | 저장 위치 |
|-----------|-----------|
| 스크래핑 결과 (블로그) | `output/{blog_id}/` |
| 스크래핑 결과 (유튜브) | `output/yt_{handle}/` |
| 블로그 글 (초안) | `docs/blog/` |
| 블로그 리뷰 | `docs/reviews/` |
| 클리핑 글 | `docs/clips/` |
| 글쓰기 참조 | `docs/context/` |

## 상태 파일

| 파일 | 용도 |
|------|------|
| `config/.last_search.json` | 마지막 검색 블로그 ID |
| `config/.favorites.json` | 즐겨찾기 목록 |
| `config/.active_persona.json` | 현재 활성 페르소나 |
| `config/personas/*.json` | 페르소나별 설정 파일 |

---

## 블크업 12기 커리큘럼 연계

| 회차 | 주제 | 실습 기능 |
|------|------|-----------|
| 1회 | 경쟁 블로그 분석하기 | `/search` + `/review` 전체분석 |
| 2회 | 나만의 페르소나 만들기 | `/persona create` 인터뷰 |
| 3회 | 키워드 전략 세우기 | `/keyword` |
| 4회 | AI와 함께 글쓰기 | `/write` + Clean Text Mode |

---

> 💡 **더 많은 기능이 필요하신가요?**
>
> - **성장 분석** (이전 분석과 비교)
> - **HTML 리포트** (고객 납품용)
> - **브릿지 콘텐츠** (주제 연결 전략)
> - **트렌드 분석** (골든키워드 발굴)
>
> 챌린지/더블업 과정에서 만나보세요!
