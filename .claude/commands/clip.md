# 블로그 글 클리핑

인자: $ARGUMENTS

읽어온 블로그 글을 참고용 md 파일로 저장합니다.

## 사용법 분기

**인자 분석:**
- 인자 없음 → 최근 읽은 블로그 글 저장
- `list` → 저장된 클립 목록 보기
- `<번호>` → 해당 클립을 VSCode에서 열기
- `#<태그>` → 태그로 필터링

## 성능 최적화

**핵심 원칙:** 모든 작업은 이 대화창 안에서 완료. 사용자가 직접 폴더를 열 필요 없음.

1. **목록 조회 (`list`)**:
   - Glob으로 파일 목록만 빠르게 조회
   - 각 파일의 frontmatter에서 필요한 정보만 추출 (첫 25줄)
   - 테이블 + 번호 안내

2. **파일 열기 (`<번호>`)**:
   - `code` 명령으로 VSCode에서 직접 열기
   - 명령: `code "파일경로"`

3. **인덱스 캐싱**:
   - 클립 저장 시 `config/.clips_index.json`에 메타데이터 저장
   - list 호출 시 인덱스 파일 먼저 확인 (없으면 생성)

## 실행 방법

### 1. 클립 저장 (인자 없음)

**전제조건:** 대화에서 블로그 글을 읽어온 상태여야 함

**저장 흐름:**
1. 현재 대화에서 읽은 블로그 정보 확인
2. AskUserQuestion으로 질문:
   - 용도: 참고 / 인용 / 벤치마킹 / 영감
   - 분류: 콘텐츠기획 / 글쓰기 / 마케팅 / 기타
3. 파일 생성: `docs/clips/{제목_sanitized}.md`
4. 인덱스 업데이트: `config/.clips_index.json`

**파일 구조:**
```markdown
---
source: naver_blog
blog_id: "{blog_id}"
post_id: "{post_id}"
url: "{url}"
author: "{author}"
title: "{title}"
created_at: "{created_at}"
clipped_at: "{clipped_at}"
purpose: "{용도}"
category: "{분류}"
tags: [{태그들}]
---

# {title}

> 원본: {url}
> 작성자: {author}
> 작성일: {created_at}

---

{본문 내용}
```

### 2. 클립 목록 보기 (`list`)

**실행 순서:**
1. `config/.clips_index.json` 확인
2. 없으면 Glob + Read로 인덱스 생성
3. 테이블 출력

**출력 형식:**
```
## 저장된 클립 (N개)

| # | 제목 | 작성자 | 분류 | 용도 | 저장일 |
|---|------|--------|------|------|--------|
| 1 | 제목1 | 작성자1 | 글쓰기 | 참고 | 2026-02-11 |

---
`/clip 1` - 파일 열기
`/clip #글쓰기` - 태그 필터
```

### 3. 클립 열기 (`<번호>`)

해당 번호의 클립 파일을 VSCode에서 직접 엽니다.

**실행:**
```bash
code "e:\Project\vibecode\Naver Scraping\docs\clips\{파일명}.md"
```

**출력:**
```
클립 #{번호} 열었습니다: {제목}
```

### 4. 태그 필터링 (`#<태그>`)

인덱스에서 해당 태그가 있는 클립만 필터링하여 목록 표시.

## 인덱스 파일 구조

`config/.clips_index.json`:
```json
{
  "clips": [
    {
      "id": 1,
      "filename": "톡방으로_전달되는_영상의_가치.md",
      "title": "톡방으로 전달되는 영상의 가치",
      "author": "띵큐",
      "category": "글쓰기",
      "purpose": "영감",
      "tags": [],
      "clipped_at": "2026-02-11"
    }
  ],
  "updated_at": "2026-02-12T16:30:00"
}
```

## AskUserQuestion 질문 구성

```json
{
  "questions": [
    {
      "question": "어떤 용도로 사용하시나요?",
      "header": "용도",
      "options": [
        {"label": "참고", "description": "나중에 참고할 자료"},
        {"label": "인용", "description": "글 작성 시 인용할 내용"},
        {"label": "벤치마킹", "description": "글쓰기 스타일 벤치마킹"},
        {"label": "영감", "description": "아이디어/영감 얻기"}
      ],
      "multiSelect": false
    },
    {
      "question": "어떤 분류에 넣을까요?",
      "header": "분류",
      "options": [
        {"label": "콘텐츠기획", "description": "콘텐츠 기획 관련"},
        {"label": "글쓰기", "description": "글쓰기 기법/스타일"},
        {"label": "마케팅", "description": "마케팅/홍보 관련"},
        {"label": "기타", "description": "그 외 분류"}
      ],
      "multiSelect": false
    }
  ]
}
```

## 참조 파일
- `docs/clips/`: 클립 저장 폴더
- `config/.clips_index.json`: 클립 인덱스 (빠른 조회용)
