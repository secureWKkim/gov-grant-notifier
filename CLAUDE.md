# gov-grant-notifier

## 스크래핑 셀렉터 레퍼런스

Phase 2(IRIS 파서), Phase 3(K-StartUp 파서) TDD에서 `tests/fixtures/`의 HTML 스냅샷을 파싱할 때 아래 셀렉터를 기준으로 구현한다. Phase 0에서 실제 사이트 DOM을 탐색해 확정한 값이므로 임의로 변경하지 않는다.

---

### IRIS (`iris_sample.html`)

| 항목 | 셀렉터 / 방법 |
|---|---|
| 목록 컨테이너 | `.tstyle.list.biz_announce ul.dbody > li` |
| 제목 | `strong.title a` innerText |
| 공고일자 | `span.ancmDe` innerText → `"공고일자 :"` 제거 후 strip |
| 기관 | `span.inst_title` innerText |
| 공모유형 | `span.pbofrTpSeNmLst` innerText → `"공모유형 :"` 제거 후 strip |
| 공고 ID | `strong.title a` onclick 속성 정규식 `'(\d+)'` 첫 번째 캡처 |
| 상태코드 | onclick 속성 정규식 `'(\w+)'\s*\)` 두 번째 캡처 (`ancmIng` / `ancmPre` / `ancmEnd`) |
| 상세 URL | `https://www.iris.go.kr/contents/retrieveBsnsAncmView.do?ancmId={id}&ancmPrg={status}` |
| 다음 페이지 | `.paginate .page_next` 클릭 (이벤트 리스너 방식, onclick은 `(n); return false;` 형태) |

**날짜 필터 전략:** 목록은 최신순 정렬. 페이지를 순회하며 `공고일자 == 어제` 항목만 수집하고, 어제보다 오래된 항목이 나오면 순회 중단.

---

### K-StartUp (`kstartup_sample.html`)

| 항목 | 셀렉터 / 방법 |
|---|---|
| 목록 항목 | `li:has(p.tit)` (또는 `li.notice`) |
| 제목 | `p.tit` innerText |
| 지원분야 | `span.flag:not(.day)` 중 첫 번째 innerText (`.flag.type01` 등 type 번호 무관) |
| 등록일자 | `span.list` 중 `"등록일자"` 포함 요소 → `"등록일자 "` 제거 후 strip |
| 마감일자 | `span.list` 중 `"마감일자"` 포함 요소 → `"마감일자 "` 제거 후 strip |
| 기관 | `span.list` 중 두 번째 요소 innerText (아이콘 `<i>` 제외) |
| 공고 ID | `a[href*="go_view"]` href 정규식 `go_view\((\d+)\)` |
| 상세 URL | `https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do?schM=view&pbancSn={id}` |
| 다음 페이지 | `.paginate .btn.next` 클릭 (`fn_egov_link_page(n)` 방식) |

**날짜 필터 전략:** 목록은 공고등록순(최신순) 정렬. `등록일자 == 어제` 항목만 수집. K-StartUp은 마감일자가 목록에 포함되므로 별도 상세 페이지 방문 불필요.
