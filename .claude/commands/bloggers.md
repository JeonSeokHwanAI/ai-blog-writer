# 블로거 목록 관리

인자: $ARGUMENTS

`config/blogs.json` 파일에 저장된 블로그 목록을 관리합니다.

## 빠른 조회 (CLI 사용)

**다음 명령은 Python CLI를 실행하여 즉시 결과를 출력합니다:**

```bash
python utils/bloggers_cli.py <인자>
```

| 인자 | CLI로 처리 | 예시 |
|------|-----------|------|
| `all` | O | `python utils/bloggers_cli.py all` |
| `<키워드>` | O | `python utils/bloggers_cli.py 비움` |
| `#<주제>` | O | `python utils/bloggers_cli.py #IT` |
| `@<ID>` | O | `python utils/bloggers_cli.py @hhey0510` |
| `add`, `del`, `update`, `history`, `categories` | X (AI 처리) | - |
| `?<별명>` | X (WebSearch 필요) | - |

**실행 방법:**
1. 위 표에서 "CLI로 처리: O"인 경우 → Bash로 CLI 실행
2. CLI 결과를 그대로 사용자에게 출력
3. "CLI로 처리: X"인 경우 → 아래 상세 지침 따름

---

## 성능 최적화

**캐싱 전략:** 블로그 목록이 100개 이상일 수 있으므로 효율적으로 처리합니다.

1. **파일 읽기 최소화**: 세션 내 첫 호출 시만 `config/blogs.json` 읽기
2. **변경 시에만 갱신**: `add`, `del` 명령 실행 후에만 캐시 갱신
3. **인덱싱 활용**: ID, 주제별로 빠른 검색을 위해 구조화된 접근

**검색 최적화:**
- 키워드 검색: ID → name → description → topics 순서로 매칭
- 주제 필터: topics 필드 직접 매칭 (부분 문자열 포함)
- 대소문자 무시 검색

## 사용법 분기

**인자 분석:**
- 인자 없음 → 대화형 메뉴 표시 (AskUserQuestion 사용)
- 숫자 (1-99) → 해당 번호 블로그 열기
- `add <ID>` → 새 블로그 추가
- `del <ID>` → 블로그 삭제
- `update <ID>` → 분석 결과 기반 블로그 정보 업데이트
- `history <ID>` → 블로그 변경 이력 조회
- `categories list` → 카테고리 캐시 현황 조회
- `categories <ID>` → 블로그 카테고리 수집/조회
- `categories <ID> analyze` → 카테고리 구조 개편 추천
- `categories <ID> classify <카테고리번호>` → 포스트 재분류 추천
- `#<주제>` → 주제로 필터링
- `@<ID>` → ID로 검색 (등록된 블로그)
- `?<별명>` → 네이버에서 별명으로 블로거 검색
- `?@<ID>` → 블로그 ID로 직접 조회 (미등록 블로그)
- `*` → 즐겨찾기만 보기
- `+<ID>` → 즐겨찾기 추가
- `-<ID>` → 즐겨찾기 제거
- `p<N>` 또는 `<N>-<M>` → 페이지/범위 보기
- 그 외 텍스트 → 키워드 검색 (등록된 블로그 내)

## 실행 방법

### 1. 사용법 안내 (인자 없음)

`config/blogs.json`을 읽지 않고, 바로 텍스트로 사용법만 표시:

```
## 어떤 작업을 하실건가요?

| # | 명령 | 설명 |
|---|------|------|
| 1 | `/bloggers *` | 즐겨찾기 |
| 2 | `/bloggers recent` | 최근 검색 10개 |
| 3 | `/bloggers all` | 전체 목록 |
| 4 | `/bloggers #<주제>` | 주제별 필터 |
| 5 | `/bloggers <키워드>` | 키워드 검색 (등록된 블로그) |
| 6 | `/bloggers @<ID>` | ID로 검색 |
| 7 | `/bloggers ?<별명>` | 별명으로 블로거 검색 |
| 8 | `/bloggers ?@<ID>` | ID로 블로그 직접 조회 |
| 9 | `/bloggers +<ID>` | 즐겨찾기 추가 |
| 10 | `/bloggers add <ID>` | 새 블로그 추가 |
| 11 | `/bloggers del <ID>` | 블로그 삭제 |
| 12 | `/bloggers update <ID>` | 분석 기반 정보 업데이트 |
| 13 | `/bloggers history <ID>` | 변경 이력 조회 |
| 14 | `/bloggers categories <ID>` | 카테고리 수집/조회 |
| 15 | `/bloggers categories <ID> analyze` | 카테고리 개편 추천 |
| 16 | `/bloggers categories list` | 캐시 현황 조회 |
| 17 | `/bloggers categories <ID> classify <번호>` | 포스트 재분류 추천 |
```

### 2. 블로그 열기 (숫자)
해당 번호의 블로그 URL을 `start` 명령으로 브라우저에서 열기.

### 3. 새 블로그 추가 (`add <ID>`)
1. 네이버 블로그 페이지에서 블로그명 가져오기 (Python 스크립트 사용)
2. 포스트 내용 기반으로 주제 자동 분류 제안
3. `config/blogs.json`에 추가
4. 메모리 파일 업데이트

### 4. 블로그 삭제 (`del <ID>`)
등록된 블로그를 삭제합니다.

**실행 방법:**
1. `config/blogs.json`에서 해당 ID 확인
2. 삭제 전 블로그 정보 표시
3. 확인 후 삭제 실행
4. `config/.favorites.json`에서도 제거 (있다면)
5. 메모리 파일 업데이트

**출력 형식:**
```
## 블로그 삭제: <ID>

| 항목 | 내용 |
|------|------|
| ID | <ID> |
| 블로그명 | ... |
| 주제 | ... |

삭제 완료되었습니다.
```

**예시:**
- `/bloggers del questioncue` - questioncue 블로그 삭제

### 5. 블로그 정보 업데이트 (`update <ID>`)
전체 분석 결과를 기반으로 블로거 정보를 업데이트합니다.

**실행 방법:**
1. `docs/reviews/{ID}_전체분석_*.md` 파일에서 최신 분석 데이터 로드
2. 분석 결과의 주제 분포, 브랜딩 정보 추출
3. 현재 `config/blogs.json` 정보와 비교
4. 변경 사항 표시 및 확인 후 업데이트
5. **변경 이력을 `config/.blogger_history.json`에 저장**

**출력 형식:**
```
## 블로거 정보 업데이트: <ID>

### 변경 사항 비교

| 항목 | 현재 | 분석 결과 (제안) |
|------|------|------------------|
| 설명 | ... | ... |
| 주제(메인) | ... | ... |
| 주제(서브) | ... | ... |

업데이트를 적용하시겠습니까?
```

**분석 데이터 매핑:**
- **설명**: 분석의 "주제 분포" 상위 3개를 조합하여 생성
- **주제(메인)**: 분석의 주요 주제를 네이버 카테고리에 매핑
- **주제(서브)**: 분석의 세부 주제들을 네이버 서브 카테고리에 매핑

**변경 이력 저장:**
업데이트 적용 시 `config/.blogger_history.json`에 기록:
```json
{
  "zeroenter": [
    {
      "date": "2026-02-12",
      "analysis_file": "docs/reviews/zeroenter_전체분석_20260212.md",
      "overall_score": 89,
      "changes": {
        "description": {"from": "...", "to": "..."},
        "topics.sub": {"from": [...], "to": [...]}
      }
    }
  ]
}
```

**예시:**
- `/bloggers update zeroenter` - zeroenter 정보 업데이트

### 6. 변경 이력 조회 (`history <ID>`)
블로거 정보 변경 이력을 조회합니다.

**실행 방법:**
1. `config/.blogger_history.json`에서 해당 ID 이력 로드
2. 날짜순으로 정렬하여 표시

**출력 형식:**
```
## 블로거 변경 이력: zeroenter

| 날짜 | 점수 | 변경 항목 |
|------|------|-----------|
| 2026-02-12 | 89 | 블로그명, 설명, 주제(서브) |
| 2026-01-15 | 82 | 설명 |

### 2026-02-12 변경 내역

| 항목 | 이전 | 이후 |
|------|------|------|
| 블로그명 | 지식의 대장장이가 알려주는 AI | 지식의 대장장이 |
| 설명 | AI 활용, 바이브 코딩... | AI 바이브코딩, 비전공자... |
| 주제(서브) | IT·컴퓨터 | IT·컴퓨터, 교육·학문 |

분석 파일: docs/reviews/zeroenter_전체분석_20260212.md
```

**예시:**
- `/bloggers history zeroenter` - zeroenter 변경 이력 조회
- `/bloggers history` - 전체 변경 이력 요약

### 7. 주제 필터링 (`#<주제>`)
`config/naver_topics.json` 참조하여 해당 주제의 블로그만 필터링 표시.
예: `/bloggers #IT·컴퓨터`

주제 선택 시 대분류만 선택하면 바로 목록 표시 (소분류 단계 생략).

### 5. ID 검색 (`@<ID>`)
정확한 ID 매칭으로 블로그 정보 상세 표시.

### 6. 키워드 검색 (그 외)
블로그명, 설명, 주제에서 키워드 포함 여부로 필터링.
등록된 블로그 내에서만 검색합니다.

### 6-1. 별명으로 블로거 검색 (`?<별명>`)
등록되지 않은 블로거를 별명/닉네임으로 네이버에서 검색합니다.

**실행 방법:**
1. WebSearch로 `네이버 블로그 "<별명>" 블로거` 검색
2. 검색 결과에서 블로그 URL 추출
3. 블로그 ID, 블로그명, 주제 정보 표시

**출력 형식:**
```
## 네이버 검색 결과: 별명 "<별명>"

| # | ID | 블로그명 | 별명 | URL |
|---|-----|----------|------|-----|
| 1 | ... | ...      | ...  | ... |

---
💡 `/bloggers add <ID>` - 블로그 등록
💡 `/bloggers ?@<ID>` - ID로 직접 조회
```

**예시:**
- `/bloggers ?띵큐` - "띵큐" 별명 블로거 검색
- `/bloggers ?육아 띵큐` - 육아 분야 "띵큐" 블로거
- `/bloggers ?맛집 리뷰어` - 맛집 리뷰어 블로거 검색

### 6-2. ID로 블로그 직접 조회 (`?@<ID>`)
블로그 ID를 알고 있을 때 직접 조회합니다.

**실행 방법:**
1. `https://blog.naver.com/<ID>` 접근
2. 블로그명, 별명, 소개글, 주제 추출
3. 등록 여부 확인

**출력 형식:**
```
## 블로그 조회: @<ID>

| 항목 | 내용 |
|------|------|
| ID | <ID> |
| 블로그명 | ... |
| 별명 | ... |
| 소개 | ... |
| URL | https://blog.naver.com/<ID> |
| 등록 여부 | 미등록 |

---
💡 `/bloggers add <ID>` - 블로그 등록
```

**예시:**
- `/bloggers ?@questioncue` - questioncue 블로그 조회
- `/bloggers ?@zeroenter` - zeroenter 블로그 조회

### 7. 즐겨찾기 (`*`)
`config/.favorites.json` 파일에서 즐겨찾기 목록만 표시.

### 8. 즐겨찾기 추가/제거 (`+<ID>`, `-<ID>`)
- `+zeroenter` → 즐겨찾기에 추가
- `-zeroenter` → 즐겨찾기에서 제거

`config/.favorites.json` 파일 형식:
```json
["zeroenter", "ari_school", "980207"]
```

### 10. 카테고리 캐시 현황 (`categories list`)

등록된 블로거들의 카테고리 캐시 현황을 표시합니다.

**실행 방법:**

1. `config/blogs.json`에서 전체 블로거 목록 로드
2. 각 블로거별 `output/{ID}/{ID}_categories.json` 존재 여부 확인
3. 캐시가 있으면 `fetched_at`, 카테고리 수, 포스트 수 표시

**출력 형식:**
```
## 카테고리 캐시 현황

| # | ID | 블로그명 | 카테고리 | 포스트 | 수집일 |
|---|-----|----------|----------|--------|--------|
| 1 | zeroenter | 지식의 대장장이 | 23 | 304 | 2026-02-26 |
| 2 | ari_school | 리리스쿨 | 12 | 180 | 2026-02-20 |
| 3 | 980207 | 비움 | - | - | 미수집 |

수집됨: 2/3 | 미수집: 1/3
```

**예시:**
- `/bloggers categories list` - 전체 캐시 현황

### 10-0. 카테고리 수집/조회 (`categories <ID>`)
블로그 카테고리 구조를 수집하고 캐시합니다.

**실행 방법:**

1. 캐시 확인: `output/{ID}/{ID}_categories.json` 존재 여부
   - 있으면 → 캐시 데이터 로드 후 표시, "갱신하시겠습니까?" 질문
   - 없으면 → 바로 수집 실행

2. 수집 실행 (Python 스크립트):
   ```python
   from scraper import NaverBlogScraper
   scraper = NaverBlogScraper(blog_id)
   categories = scraper.get_categories()
   ```

3. 결과를 `output/{ID}/{ID}_categories.json`에 저장:
   ```json
   {
     "blog_id": "<ID>",
     "fetched_at": "2026-02-26",
     "total_posts": 304,
     "categories": [
       {"no": "58", "name": "AI 바이브코딩", "count": 53, "parent_no": "0"},
       {"no": "54", "name": "TechTip", "count": 55, "parent_no": "50"}
     ]
   }
   ```

4. 트리 형태로 출력

**출력 형식:**
```
## 블로그 카테고리: {blog_id}

수집일: {fetched_at} | 총 {total_posts}개 포스트

### 카테고리 트리

📁 전체 ({total_posts})
├── 📂 [50] 부모카테고리 ({count})
│   ├── 📄 [54] 자식카테고리1 ({count})
│   └── 📄 [51] 자식카테고리2 ({count})
├── 📄 [55] 독립카테고리 ({count})
└── ...

---
💡 `/bloggers categories {ID}` - 카테고리 갱신
💡 `/bloggers categories {ID} classify <번호>` - 포스트 재분류
💡 `/write` 시 카테고리 추천에 활용됩니다
```

**트리 구성 규칙:**
- `parent_no`가 `"0"`인 카테고리 → 루트 레벨
- `parent_no`가 다른 카테고리의 `no`와 일치 → 해당 카테고리의 하위
- 부모 카테고리의 count = 자기 포스트 수 + 하위 카테고리 포스트 합산

**예시:**
- `/bloggers categories zeroenter` - zeroenter 카테고리 수집
- `/bloggers categories ari_school` - ari_school 카테고리 수집

### 10-1. 카테고리 구조 개편 추천 (`categories <ID> analyze`)

수집된 카테고리 데이터를 분석하여 구조 개편을 제안합니다.

**실행 방법:**

1. `output/{ID}/{ID}_categories.json` 캐시 로드 (없으면 먼저 수집)
2. 아래 분석 규칙으로 문제점 진단
3. 개선안 제시 (BEFORE → AFTER 비교)

**분석 규칙:**

| 규칙 | 조건 | 제안 |
|------|------|------|
| 소규모 카테고리 | 포스트 3개 이하 | 유사 카테고리에 통합 |
| 대규모 카테고리 | 포스트 50개 이상 | 하위 카테고리로 분리 |
| 유사 카테고리 | 이름이 비슷하거나 주제 겹침 | 하나로 통합 |
| 고아 부모 | 하위 1개뿐인 부모 카테고리 | 계층 단순화 |
| 깊은 중첩 | 3단계 이상 중첩 | 2단계로 평탄화 |

**출력 형식:**
```
## 카테고리 구조 분석: {blog_id}

### 진단 결과

| # | 유형 | 대상 | 번호 | 포스트 수 | 제안 |
|---|------|------|------|-----------|------|
| 1 | 소규모 | 직장생활 | [53] | 4 | → "1퍼센트 IT"에 통합 |
| 2 | 대규모 | AI로 돈벌기 | [58] | 100 | → 하위 카테고리 분리 |
| 3 | 유사 | PC지식 + TechTip | [51]+[54] | 18+55 | → "IT 팁" 통합 고려 |

### 개편안

**현재** ({N}개 카테고리)
📁 전체
├── 📂 [50] 기존 구조...

**제안** ({M}개 카테고리)
📁 전체
├── 📂 [50] 개편 구조...

---
💡 이 제안은 참고용입니다. 네이버 블로그에서 직접 수정하세요.
💡 `/bloggers categories {ID} classify <번호>` - 특정 카테고리 포스트 재분류
```

**예시:**
- `/bloggers categories zeroenter analyze` - zeroenter 카테고리 개편 추천

### 10-2. 포스트 재분류 (`categories <ID> classify <카테고리번호>`)

특정 카테고리의 포스트들을 분석하여 어느 카테고리로 이동하면 좋을지 추천합니다.

**실행 방법:**

1. `output/{ID}/{ID}_categories.json` 캐시 로드 (없으면 먼저 수집)
2. 해당 카테고리의 포스트 목록 수집:
   ```python
   from scraper import NaverBlogScraper
   scraper = NaverBlogScraper(blog_id)
   posts = scraper.get_posts_by_category(category_no)
   ```
3. 전체 카테고리 목록과 각 포스트 제목을 비교하여 재분류 추천
4. 결과를 표로 출력

**분류 기준:**
- 포스트 제목의 키워드와 각 카테고리 이름/주제의 관련성
- 현재 카테고리에 유지할 글 vs 다른 카테고리로 이동할 글 구분
- 이동 추천 시 대상 카테고리와 이유 명시

**출력 형식:**
```
## 포스트 재분류: {blog_id} > {카테고리명} ({count}개)

### 이동 추천

| # | 제목 | 현재 | 추천 카테고리 | 이유 |
|---|------|------|---------------|------|
| 1 | 포스트 제목... | 카테고리A | 카테고리B | 주제가 B에 더 적합 |
| 2 | ... | ... | ... | ... |

### 현재 카테고리 유지 ({N}개)

| # | 제목 |
|---|------|
| 1 | 유지할 포스트... |

---
💡 이 제안은 참고용입니다. 네이버 블로그에서 직접 이동하세요.
```

**예시:**
- `/bloggers categories zeroenter classify 54` - TechTip 포스트 재분류
- `/bloggers categories zeroenter classify 58` - AI 바이브코딩 포스트 재분류

### 9. 페이지/범위 보기 (`p<N>`, `<N>-<M>`)
- `p2` → 21~40번 표시 (페이지당 20개)
- `1-20` → 1~20번 표시
- `50-60` → 50~60번 표시

## 출력 형식

목록 표시 시 항상 마크다운 표 사용:

```
## 블로그 목록 (필터: 즐겨찾기 / N개)

| # | ID | 블로그명 | 설명 | 주제 |
|---|-----|----------|------|------|
| 1 | ... | ...      | ...  | ...  |

---
💡 `/bloggers <번호>` - 블로그 열기
💡 `/bloggers +<ID>` - 즐겨찾기 추가
```

## 참조 파일
- `config/blogs.json`: 블로그 메타데이터
- `config/naver_topics.json`: 네이버 주제 카테고리
- `config/.favorites.json`: 즐겨찾기 목록
- `config/.last_searches.json`: 최근 검색 기록
- `output/{blog_id}/{blog_id}_categories.json`: 블로그 카테고리 캐시

## 최근 검색 기록

`/search` 또는 `/review` 실행 시 `config/.last_searches.json`에 기록:
```json
{
  "searches": [
    {"id": "zeroenter", "timestamp": "2024-01-15T10:30:00"},
    {"id": "ari_school", "timestamp": "2024-01-14T15:20:00"}
  ]
}
```
최대 20개까지 저장, 오래된 것은 자동 삭제.
