# Product Requirements Document (PRD)

## 1. Overview

**Feature / Project Name:** 정부 지원사업 텔레그램 알림 봇 (gov-grant-notifier)

**Problem Statement:**
스타트업 대표는 매일 쏟아지는 수많은 정부 지원사업(K-Startup 등) 공고를 일일이 모니터링하기 어렵습니다. 중요한 공고를 놓치면 사업 기회를 잃게 되지만, 매일 여러 사이트를 방문해 탐색하는 것은 리소스 소모가 큽니다.

**Proposed Solution:**
매일 오전 10시, 전날 새로 등록된 정부 지원사업 공고들을 스크래핑하여 스타트업 대표의 텔레그램으로 바로 받아볼 수 있는 가볍고 신뢰성 높은 텔레그램 알림 봇을 구축합니다.

**AI Build Summary:**
> Build a lightweight Python automation script that runs daily at 10:00 AM KST via GitHub Actions. The script uses Playwright to scrape new government grant announcements (e.g., from K-Startup) posted on the previous day and sends them to a configured Telegram channel/chat using the Telegram Bot API. Keep it state-free or use simple file-based state if needed, running with zero hosting costs.

---

## 2. Goals & Success Metrics

**Primary Goal:**
- 매일 오전 10시(KST)에 누락 없이 전날 등록된 새로운 공고를 텔레그램 메시지로 수신함.

**Success Metrics:**
- **발송 성공률:** 99% 이상 (스크래핑 차단 또는 네트워크 에러 외 항시 전송 성공)
- **정보 신속성:** 전날(D-1) 등록된 모든 신규 공고가 빠짐없이 포함됨.

**Anti-goals:**
- 복잡한 사용자 대시보드나 회원가입 웹페이지 구축 없음.
- 알림 수신 대상자의 맞춤 필터링 검색(키워드 설정 등) 기능은 MVP 단계에서 제외 (전체 신규 공고 발송).

---

## 3. Scope & Constraints

**In scope:**
- K-Startup(또는 주요 정부 지원사업 통합 공고 페이지) 대상 Playwright 기반 스크래핑.
- 공고 작성일이 '어제(D-1)'인 신규 공고 필터링.
- 텔레그램 봇 API를 통한 메시지 전송 기능.
- 메시지 포맷팅: 공고 제목, 지원 분야, 마감일, 상세 링크 포함.
- GitHub Actions를 이용한 매일 오전 10시(KST) 스케줄링 실행.

**Out of scope:**
- 개별 사용자별 키워드 구독/맞춤 설정 기능.
- 별도의 DB 구축 (Supabase, MySQL 등) 및 관리.
- 사용자용 UI/웹 애플리케이션 화면.

**Technical constraints:**
- **언어 및 라이브러리:** Python 3.x, Playwright, Requests (Telegram API 호출용).
- **무비용 운영:** 별도의 유료 서버 호스팅 없이 GitHub Actions (Cron) 및 텔레그램 무료 봇 채널 활용.
- **지역/시간대:** 한국 시간 기준 매일 오전 10시 (GitHub Actions Cron의 UTC 기준 설정 및 스크립트 내 한국 시간 처리 필요).

---

## 4. Jobs to Be Done (JTBD)

| Priority | Job Statement |
|----------|---------------|
| 1 | 스타트업 대표로서, 나는 매일 아침 전날 새로 올라온 정부 지원 공고 목록을 카톡/텔레그램처럼 편한 채널로 받아보고 싶다. (여러 사이트를 직접 방문하기 번거롭기 때문) |
| 2 | 스크래핑 실패나 텔레그램 전송에 문제가 생겼을 때, 개발자(또는 관리자)는 알림이 끊겼음을 즉시 인지하여 대처할 수 있어야 한다. |

---

## 5. Tech Stack Recommendation

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Language** | Python 3.11+ | 스크래핑 라이브러리 생태계가 풍부하고, 경량 자동화 스크립트 작성에 최적화됨. |
| **Scraper** | Playwright (Python) | 동적 웹사이트 및 Cloudflare 등 기본적인 크롤링 차단 요소를 우회하며 동적 렌더링 페이지를 빠르고 안정적으로 긁어올 수 있음. |
| **Notification** | Telegram Bot API (`httpx`) | 가볍고 무료이며 채널이나 갠톡으로 포맷팅된 메시지 전송이 용이함. |
| **Scheduler** | GitHub Actions (Cron) | 매일 10시 실행 스케줄러를 비용 없이 안전하게 유지할 수 있음. |

---

## 6. Suggested File Structure

```text
gov-grant-notifier/
├── .github/
│   └── workflows/
│       └── daily_notify.yml    # 매일 10시 스케줄링 실행을 위한 GitHub Actions 워크플로우
├── src/
│   ├── __init__.py
│   ├── scraper.py              # Playwright 기반 스크래핑 엔진
│   ├── telegram_bot.py         # 텔레그램 메시지 전송 모듈
│   └── main.py                 # 실행 엔트리포인트 (시간 계산, 데이터 조합, 전송 흐름 제어)
├── requirements.txt            # 의존성 패키지 리스트 (playwright, httpx 등)
├── PRD.md                      # 본 문서
└── README.md                   # 실행 방법 설명서
```

---

## 7. 놓치기 쉬운 엣지 케이스 및 제안 사항 (Suggested Checklist)

1. **공고가 올라오지 않은 경우 (Empty State):**
   - 금요일 10시 발송 이후 토/일요일 혹은 공휴일에는 새로운 공고가 올라오지 않을 수 있습니다.  발송 에러가 난 경우가 아닌 이상, 새 공고가 없다고 해서 공고가 없음을 알리는  메시지를 보낼 필요는 없습니다.
2. **텔레그램 메시지 길이 제한 (Telegram API Constraint):**
   - 텔레그램 단일 메시지는 최대 4096자 제한이 있습니다. 공고가 한 번에 많이 올라오는 경우(예: 월요일 아침 또는 매월 초) 글자 수 초과로 전송이 실패할 수 있습니다.
   - **대응안:** 전송할 메시지 내용이 4000자를 넘을 경우, 메시지를 쪼개서 분할 전송하는 로직을 `telegram_bot.py`에 적용합니다.
3. **스크래핑 대상 사이트 구조 변경 (Scraping Breakage):**
   - 정부 사이트(K-Startup 등)는 개편되거나 DOM 구조가 변경되는 일이 잦습니다. 이 경우 셀렉터가 깨져 정보 수집에 실패합니다.
   - **대응안:** 스크래핑 과정에서 Exception 발생 시, GitHub Actions 실행이 실패 상태로 기록되거나 관리자 텔레그램으로 `"크롤러 장애 발생"` 에러 로그 알림을 보내도록 설계합니다.
4. **상태 관리의 부재 (State-free):**
   - 단순히 "전날(어제) 날짜" 정보로만 필터링할 경우, 실시간 수집 시점 차이로 인해 23시 59분에 등록된 공고 등이 누락될 수 있습니다.
   - **대응안:** 새로운 공고가 더 이상 등록되지 않는 새벽 시간대(예: 새벽 3시)에 실행하여 전날(어제) 등록된 공고 전체를 수집하도록 설계합니다. 이를 통해 어제 날짜의 공고가 완전히 마감된 상태에서 수집하므로, 별도의 상태 저장(DB 등) 없이도 누락이나 중복 없이 안전하게 수집할 수 있습니다.
