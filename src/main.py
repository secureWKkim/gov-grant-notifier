import os
from datetime import datetime, timezone, timedelta, date

from src.scraper import parse_iris, parse_kstartup, filter_by_date
from src.telegram_bot import send_message, format_announcement, split_messages


def get_yesterday_kst() -> date:
    kst = timezone(timedelta(hours=9))
    return (datetime.now(kst) - timedelta(days=1)).date()


async def scrape_iris(yesterday: date) -> list[dict]: # async를 붙이면 코루틴으로 생성됨
    # 아래처럼 하면 playwright가 설치되지 않은 환경에서 이 함수를 호출하지 않는 한 import 에러가 나지 않음
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        # await은 다른 코루틴이 끝날 때까지 기다리도록 코드 실행 제어권을 넘기거나,
        # async가 붙은 코루틴 객체를 '실행'시킬 때 쓰는 문법이다. 
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(
            "https://www.iris.go.kr/contents/retrieveBsnsAncmBtinSituListView.do"
        )
        results = []
        while True:
            html = await page.content()
            all_items = parse_iris(html)
            items = filter_by_date(all_items, yesterday)
            results.extend(items)
            if not all_items or all_items[-1]["date"] < yesterday.strftime("%Y-%m-%d"):
                break
            # DOM 에서 .paginate 클래스의 .page_next 요소를 찾음
            next_btn = page.locator(".paginate .page_next")
            if await next_btn.count() == 0:
                break
            # click()은 Chromium 프로세스에 클릭 명령을 보내고(IPC 통신), 클릭 동작 자체가
            # 완료되면 반환된다. 단, 클릭으로 인해 실행되는 JavaScript AJAX 요청은 아직
            # 시작도 안 된 상태일 수 있으므로, 이 줄만으로는 다음 페이지 데이터가 준비됐다고
            # 볼 수 없다.
            await next_btn.click()
            # 클릭 후 JavaScript가 서버에 AJAX 요청을 보내고 응답을 받아 DOM을 업데이트하는
            # 과정이 끝날 때까지 기다린다. "networkidle"은 네트워크 요청이 500ms 동안 하나도
            # 없으면 완료로 판단하는 기준이다. 이 줄이 없으면 AJAX가 채 끝나기 전에
            # page.content()를 호출해 이전 페이지 HTML을 읽어버리는 버그가 생긴다.
            await page.wait_for_load_state("networkidle")
        # browser.close()는 async def로 정의돼 있어서, await 없이 호출하면
        # 코루틴 객체만 만들어지고 실제로 실행되지 않는다. await를 붙여야
        # 이벤트 루프가 이 코루틴을 실제로 실행해 Chromium에 종료 명령을 전달한다.
        await browser.close()
    return results


async def scrape_kstartup(yesterday: date) -> list[dict]:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(
            "https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do"
        )
        results = []
        while True:
            html = await page.content()
            all_items = parse_kstartup(html)
            items = filter_by_date(all_items, yesterday)
            results.extend(items)
            if not all_items or all_items[-1]["date"] < yesterday.strftime("%Y-%m-%d"):
                break
            next_btn = page.locator(".paginate .btn.next")
            if await next_btn.count() == 0:
                break
            await next_btn.click()
            await page.wait_for_load_state("networkidle")
        await browser.close()
    return results


async def run() -> list[dict]:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    yesterday = get_yesterday_kst()

    try:
        # asyncio.gather 함수를 이용해 둘을 한 번에 코루틴으로 넘기면 병렬성이 높아진다.
        # 논리 레벨에서 그렇다는 거고, 파이썬 특성상 물리 레벨에서 그런 것은 아니다.
        # 파이썬은 멀티스레딩, asyncio는 CPU 병렬 처리가 안되기 때문 (멀티스레딩은 GIL 때문)
        # 그걸 하려면 멀티프로세싱 사용해야 됨
        iris_items = await scrape_iris(yesterday)
        kstartup_items = await scrape_kstartup(yesterday)
    except Exception as e:
        await send_message(token=token, chat_id=chat_id, text=f"오류: {e}")
        return []

    items = iris_items + kstartup_items

    if not items:
        return []

    for item in items:
        for chunk in split_messages(format_announcement(item)):
            await send_message(token=token, chat_id=chat_id, text=chunk)

    return items


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())


"""
[asyncio가 유리한 점]
컨텍스트 스위칭 비용이 거의 없어요. 멀티스레딩의 컨텍스트 스위칭은 OS가 개입해서 레지스터 저장, 스택 교체, 캐시 무효화가 일어나요. asyncio의 코루틴 전환은 Python이 내부적으로 함수 프레임을 바꾸는 수준이라 훨씬 가벼워요.

[asyncio의 사이드 이펙트]
첫째, 한 코루틴이 CPU를 오래 잡으면 전체가 멈춰요. 멀티스레딩은 OS가 강제로 스위칭하지만, asyncio는 코루틴이 스스로 await로 양보해야 해요. 양보 안 하면 다른 코루틴이 끼어들 수 없어요.

async def 나쁜예():
    result = []
    for i in range(10_000_000):  # await 없는 CPU 집중 작업
        result.append(i * i)     # 이 동안 이벤트 루프 전체가 블로킹됨
    return result

둘째, 리소스 한계에 부딪힐 수 있어요. 파일 100개를 동시에 열면 OS의 파일 디스크립터 한도에 걸릴 수 있고, HDD라면 디스크 헤드가 100곳을 동시에 왔다갔다 해서 오히려 순차보다 느려질 수 있어요. SSD는 이 문제가 덜해요.
셋째, CPU 연산에는 아무 이점이 없어요. asyncio는 순전히 I/O 대기 시간을 겹치는 기법이에요. 연산이 무거운 작업은 멀티프로세싱(multiprocessing)을 써야 해요.


[asyncio에서 I/O가 실제로 어떻게 동작하나]
await f.read()를 만나면 Python이 직접 디스크를 기다리는 게 아니에요.

Python → OS에 "이 파일 읽으면 알려줘" 등록 → 제어권 반환
OS 커널 → 디스크 컨트롤러에 읽기 명령
디스크 → 데이터 준비 완료 → OS에 인터럽트
OS → Python 이벤트 루프에 알림 → 해당 코루틴 재개

핵심은 실제 I/O는 OS 커널이 처리한다는 거예요. 파일 100개를 gather로 등록하면, Python 스레드는 하나지만 OS는 100개의 읽기 요청을 동시에 처리할 수 있어요. Python은 그냥 알림을 기다리는 거예요.
"""