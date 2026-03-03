# 유튜버 목록 관리

인자: $ARGUMENTS

`config/youtubers.json` 파일에 저장된 유튜버 목록을 관리합니다.

## 빠른 조회 (CLI 사용)

**다음 명령은 Python CLI를 실행하여 즉시 결과를 출력합니다:**

```bash
python utils/youtubers_cli.py <인자>
```

| 인자 | CLI로 처리 | 예시 |
|------|-----------|------|
| `all` | O | `python utils/youtubers_cli.py all` |
| `<키워드>` | O | `python utils/youtubers_cli.py 테크몽` |
| `#<주제>` | O | `python utils/youtubers_cli.py #IT` |
| `@<ID>` | O | `python utils/youtubers_cli.py @yt_techmong` |
| `add`, `del`, `update`, `history` | X (AI 처리) | - |
| `?<이름>` | X (WebSearch 필요) | - |

**실행 방법:**
1. 위 표에서 "CLI로 처리: O"인 경우 → Bash로 CLI 실행
2. CLI 결과를 그대로 사용자에게 출력
3. "CLI로 처리: X"인 경우 → 아래 상세 지침 따름

---

## 성능 최적화

**캐싱 전략:**

1. **파일 읽기 최소화**: 세션 내 첫 호출 시만 `config/youtubers.json` 읽기
2. **변경 시에만 갱신**: `add`, `del` 명령 실행 후에만 캐시 갱신
3. **인덱싱 활용**: ID, 주제별로 빠른 검색을 위해 구조화된 접근

**검색 최적화:**
- 키워드 검색: ID → name → nickname → handle → description → topics 순서로 매칭
- 주제 필터: topics 필드 직접 매칭 (부분 문자열 포함)
- 대소문자 무시 검색

## 사용법 분기

**인자 분석:**
- 인자 없음 → 사용법 안내 표시
- 숫자 (1-99) → 해당 번호 채널 열기
- `add <@handle>` → 새 유튜버 추가
- `del <ID>` → 유튜버 삭제
- `update <ID>` → 분석 결과 기반 유튜버 정보 업데이트
- `history <ID>` → 유튜버 변경 이력 조회
- `#<주제>` → 주제로 필터링
- `@<ID>` → ID로 검색 (등록된 유튜버)
- `?<이름>` → 유튜브에서 채널 검색
- `*` → 즐겨찾기만 보기
- `+<ID>` → 즐겨찾기 추가
- `-<ID>` → 즐겨찾기 제거
- 그 외 텍스트 → 키워드 검색 (등록된 유튜버 내)

## 실행 방법

### 1. 사용법 안내 (인자 없음)

`config/youtubers.json`을 읽지 않고, 바로 텍스트로 사용법만 표시:

```
## 어떤 작업을 하실건가요?

| # | 명령 | 설명 |
|---|------|------|
| 1 | `/youtubers *` | 즐겨찾기 |
| 2 | `/youtubers all` | 전체 목록 |
| 3 | `/youtubers #<주제>` | 주제별 필터 |
| 4 | `/youtubers <키워드>` | 키워드 검색 |
| 5 | `/youtubers @<ID>` | ID로 검색 |
| 6 | `/youtubers ?<이름>` | 유튜브에서 채널 검색 |
| 7 | `/youtubers +<ID>` | 즐겨찾기 추가 |
| 8 | `/youtubers add <@handle>` | 새 유튜버 추가 |
| 9 | `/youtubers del <ID>` | 유튜버 삭제 |
| 10 | `/youtubers update <ID>` | 분석 기반 정보 업데이트 |
| 11 | `/youtubers history <ID>` | 변경 이력 조회 |
```

### 2. 채널 열기 (숫자)
해당 번호 유튜버의 URL을 `start` 명령으로 브라우저에서 열기.

### 3. 새 유튜버 추가 (`add <@handle>`)

YouTube API로 채널 정보를 수집하여 등록합니다.

**실행 방법:**
1. `YouTubeScraper`로 채널 정보 수집:
   ```python
   import sys, os
   sys.path.insert(0, "프로젝트_루트_경로")
   from scraper import YouTubeScraper
   scraper = YouTubeScraper(channel_input="{handle}")
   info = scraper.get_channel_info()
   ```
2. 채널 정보 표시 (채널명, 구독자, 영상 수, 설명)
3. 주제 자동 분류 제안 (AskUserQuestion으로 확인)
4. `config/youtubers.json`에 추가

**ID 생성 규칙:**
- handle에서 `@` 제거 → `yt_{handle}` 형식
- 예: `@techmong` → `yt_techmong`

**추가 확인 출력:**
```
## 유튜버 추가: @{handle}

| 항목 | 내용 |
|------|------|
| ID | yt_{handle} |
| 채널명 | {name} |
| 구독자 | {subscribers} |
| 영상 수 | {total_videos} |
| 설명 | {description} |
| 주제 | {topics.main} |

등록 완료되었습니다.

---
💡 `/search yt:{handle}` - 영상 스크래핑
💡 `/review {nickname}` - 채널 분석
```

### 4. 유튜버 삭제 (`del <ID>`)
등록된 유튜버를 삭제합니다.

**실행 방법:**
1. `config/youtubers.json`에서 해당 ID 확인
2. 삭제 전 유튜버 정보 표시
3. 확인 후 삭제 실행
4. `config/.yt_favorites.json`에서도 제거 (있다면)

**출력 형식:**
```
## 유튜버 삭제: <ID>

| 항목 | 내용 |
|------|------|
| ID | <ID> |
| 채널명 | ... |
| 구독자 | ... |
| 주제 | ... |

삭제 완료되었습니다.
```

### 5. 유튜버 정보 업데이트 (`update <ID>`)
전체 분석 결과를 기반으로 유튜버 정보를 업데이트합니다.

**실행 방법:**
1. `docs/reviews/{ID}_전체분석_*.md` 파일에서 최신 분석 데이터 로드
2. 분석 결과의 주제 분포, 구독자 수, 영상 수 추출
3. 현재 `config/youtubers.json` 정보와 비교
4. 변경 사항 표시 및 확인 후 업데이트
5. **변경 이력을 `config/.yt_history.json`에 저장**

**출력 형식:**
```
## 유튜버 정보 업데이트: <ID>

### 변경 사항 비교

| 항목 | 현재 | 분석 결과 (제안) |
|------|------|------------------|
| 구독자 | ... | ... |
| 영상 수 | ... | ... |
| 설명 | ... | ... |
| 주제(메인) | ... | ... |
| 주제(서브) | ... | ... |

업데이트를 적용하시겠습니까?
```

**변경 이력 저장:**
업데이트 적용 시 `config/.yt_history.json`에 기록:
```json
{
  "yt_techmong": [
    {
      "date": "2026-02-26",
      "analysis_file": "docs/reviews/yt_techmong_전체분석_20260226.md",
      "changes": {
        "subscribers": {"from": 929000, "to": 950000},
        "total_videos": {"from": 761, "to": 780}
      }
    }
  ]
}
```

### 6. 변경 이력 조회 (`history <ID>`)
유튜버 정보 변경 이력을 조회합니다.

**실행 방법:**
1. `config/.yt_history.json`에서 해당 ID 이력 로드
2. 날짜순으로 정렬하여 표시

**출력 형식:**
```
## 유튜버 변경 이력: yt_techmong

| 날짜 | 변경 항목 |
|------|-----------|
| 2026-02-26 | 구독자, 영상 수 |
| 2026-02-12 | 설명, 주제(서브) |

### 2026-02-26 변경 내역

| 항목 | 이전 | 이후 |
|------|------|------|
| 구독자 | 929,000 | 950,000 |
| 영상 수 | 761 | 780 |

분석 파일: docs/reviews/yt_techmong_전체분석_20260226.md
```

### 7. 주제 필터링 (`#<주제>`)
해당 주제의 유튜버만 필터링 표시.
예: `/youtubers #IT·기술`

### 8. ID 검색 (`@<ID>`)
정확한 ID 매칭으로 유튜버 정보 상세 표시.

### 9. 키워드 검색 (그 외)
채널명, 별명, 핸들, 설명, 주제에서 키워드 포함 여부로 필터링.
등록된 유튜버 내에서만 검색합니다.

### 9-1. 유튜브에서 채널 검색 (`?<이름>`)
등록되지 않은 유튜버를 유튜브에서 검색합니다.

**실행 방법:**
1. WebSearch로 `유튜브 "{이름}" 채널` 검색
2. 검색 결과에서 채널 URL, 채널명, 구독자 정보 추출
3. 결과 표시

**출력 형식:**
```
## 유튜브 검색 결과: "<이름>"

| # | 채널명 | 핸들 | 구독자 | URL |
|---|--------|------|--------|-----|
| 1 | ...    | @... | ...    | ... |

---
💡 `/youtubers add <@handle>` - 유튜버 등록
```

### 10. 즐겨찾기 (`*`)
`config/.yt_favorites.json` 파일에서 즐겨찾기 목록만 표시.

### 11. 즐겨찾기 추가/제거 (`+<ID>`, `-<ID>`)
- `+yt_techmong` → 즐겨찾기에 추가
- `-yt_techmong` → 즐겨찾기에서 제거

`config/.yt_favorites.json` 파일 형식:
```json
["yt_techmong", "yt_chocohomee"]
```

## 출력 형식

목록 표시 시 항상 마크다운 표 사용:

```
## 유튜버 목록 (필터: 전체 / N명)

| # | ID | 채널명 | 별명 | 구독자 | 영상 | 주제 |
|---|-----|--------|------|--------|------|------|
| 1 | yt_techmong | 테크몽 Techmong | 테크몽 | 92.9만 | 761 | IT·기술 |

---
💡 `/youtubers <번호>` - 채널 열기
💡 `/youtubers +<ID>` - 즐겨찾기 추가
```

## 참조 파일
- `config/youtubers.json`: 유튜버 메타데이터
- `config/.yt_favorites.json`: 유튜버 즐겨찾기
- `config/.yt_history.json`: 유튜버 변경 이력
