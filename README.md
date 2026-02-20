# AI Blog Writer

> AI는 펜이고, 당신이 작가입니다.

네이버 블로그 스크래핑, 분석, 글쓰기 도구입니다.

## 주요 기능

### 수집 및 분석
- **블로그 스크래핑** - 네이버 블로그 포스트 자동 수집
- **전체분석** - 12개 항목 종합 분석
- **특정글분석** - 8개 섹션 심층 분석
- **키워드 분석** - 연관 키워드, 검색 의도 분석
- **이달의 블로그** - 네이버 추천 블로그 수집

### 콘텐츠 생성
- **페르소나** - 나만의 글쓰기 스타일 생성/관리
- **AI 글쓰기** - 페르소나 기반 블로그 글 작성
- **클리핑** - 참고 글 마크다운 저장

## 설치 방법

### 1. 요구 사항

- Python 3.9 이상
- Claude Code (Claude Desktop)

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. Playwright 설치 (이달의 블로그 기능)

```bash
playwright install chromium
```

## 사용 방법

Claude Code에서 슬래시 명령어로 실행합니다.

### 블로그 스크래핑

```
/search <블로그ID> <수량>
```

### 블로그 분석

```
/review <블로그ID> 0        # 전체분석 (12개 항목)
/review <블로그ID> 00       # 특정글 분석
```

### 키워드 분석

```
/keyword <키워드>
```

### 페르소나 관리

```
/persona list              # 목록 보기
/persona create <이름>     # 새로 만들기 (인터뷰)
/persona <블로그ID>        # 블로그 분석으로 생성
/persona use <이름>        # 페르소나 전환
```

### 블로그 글쓰기

```
/write                     # 새 글 작성
/write <제목>              # 제목 지정 후 작성
```

## 프로젝트 구조

```
├── main.py                 # 메인 스크래퍼
├── CLAUDE.md               # Claude Code 설정
├── config/
│   ├── blogs.json          # 블로그 목록
│   ├── personas/           # 페르소나 JSON
│   └── keyword_config.json # 키워드 설정
├── scraper/                # 스크래핑 모듈
├── utils/                  # 유틸리티
├── output/                 # 스크래핑 결과
└── docs/
    ├── blog/               # 작성한 글
    ├── context/            # 페르소나 참조
    ├── reviews/            # 분석 리뷰
    └── clips/              # 클리핑
```

## 블크업 12기 커리큘럼

| 회차 | 주제 | 실습 기능 |
|------|------|-----------|
| 1회 | 경쟁 블로그 분석하기 | `/search` + `/review 0` |
| 2회 | 나만의 페르소나 만들기 | `/persona create` |
| 3회 | 키워드 전략 세우기 | `/keyword` |
| 4회 | AI와 함께 글쓰기 | `/write` |

## 전체분석 항목 (12가지)

1. 콘텐츠 장단점
2. 운영자 문제점
3. SEO 개선점
4. 전략 제안
5. 타겟 독자
6. 브랜딩
7. 발행 패턴
8. 제목 패턴
9. 수익화
10. 경쟁 환경
11. AI 대응력
12. 독자 참여도

---

Made with [Claude Code](https://claude.ai/code)

## License

MIT License
