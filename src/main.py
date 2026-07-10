import os
from datetime import datetime, timezone, timedelta, date

from src.scraper import parse_iris, parse_kstartup, filter_by_date
from src.telegram_bot import send_message, format_announcement, split_messages


def get_yesterday_kst() -> date:
    kst = timezone(timedelta(hours=9))
    return (datetime.now(kst) - timedelta(days=1)).date()


async def scrape_iris(yesterday: date) -> list[dict]:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
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
