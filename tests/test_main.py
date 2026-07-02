import os
from datetime import datetime, timezone, timedelta, date

import pytest

from src.main import run, get_yesterday_kst


ITEM_IRIS = {
    "title": "IRIS 공고",
    "inst": "한국연구재단",
    "date": "2026-07-01",
    "field": "자유공모",
    "url": "https://www.iris.go.kr/test",
}

ITEM_KSTARTUP = {
    "title": "K-StartUp 공고",
    "inst": "창업진흥원",
    "date": "2026-07-01",
    "deadline": "2026-07-31",
    "field": "사업화",
    "url": "https://www.k-startup.go.kr/test",
}

ENV = {"TELEGRAM_BOT_TOKEN": "TEST_TOKEN", "TELEGRAM_CHAT_ID": "123456"}


# ── run ───────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_run_combines_results_from_both_scrapers(mocker):
    mocker.patch("src.main.scrape_iris", return_value=[ITEM_IRIS])
    mocker.patch("src.main.scrape_kstartup", return_value=[ITEM_KSTARTUP])
    mocker.patch("src.main.send_message")
    mocker.patch.dict(os.environ, ENV)
    results = await run()
    assert len(results) == 2


@pytest.mark.asyncio
async def test_run_sends_nothing_when_no_announcements(mocker):
    mocker.patch("src.main.scrape_iris", return_value=[])
    mocker.patch("src.main.scrape_kstartup", return_value=[])
    send_mock = mocker.patch("src.main.send_message")
    mocker.patch.dict(os.environ, ENV)
    await run()
    send_mock.assert_not_called()


@pytest.mark.asyncio
async def test_run_sends_error_notification_on_scraper_failure(mocker):
    mocker.patch("src.main.scrape_iris", side_effect=Exception("timeout"))
    send_mock = mocker.patch("src.main.send_message")
    mocker.patch.dict(os.environ, ENV)
    await run()
    assert "오류" in send_mock.call_args[1]["text"]


# ── get_yesterday_kst ─────────────────────────────────────────────────────────

def test_get_yesterday_kst_returns_date_type():
    assert isinstance(get_yesterday_kst(), date)


def test_get_yesterday_kst_is_one_day_before_today_in_kst():
    kst = timezone(timedelta(hours=9))
    today_kst = datetime.now(kst).date()
    assert get_yesterday_kst() == today_kst - timedelta(days=1)
