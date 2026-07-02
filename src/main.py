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
            items = filter_by_date(parse_iris(html), yesterday)
            results.extend(items)
            all_items = parse_iris(html)
            if not all_items or all_items[-1]["date"] < yesterday.strftime("%Y-%m-%d"):
                break
            next_btn = page.locator(".paginate .page_next")
            if await next_btn.count() == 0:
                break
            await next_btn.click()
            await page.wait_for_load_state("networkidle")
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
            items = filter_by_date(parse_kstartup(html), yesterday)
            results.extend(items)
            all_items = parse_kstartup(html)
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
