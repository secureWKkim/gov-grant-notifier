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

"""마지막에 반환값의 길이만 검증하므로, 이전에 단순히 들어간 메시지 개수만 확인하던 코드는
TDD 원칙 중 'Test behavior, not implementation.' 에 위배된다. 따라서 
send_message 모킹을 하고 결과가 combine되는 행동을 확인하려면 아래와 같이 바껴야 한다.
"""
@pytest.mark.asyncio
async def test_run_combines_results_from_both_scrapers(mocker):
    mocker.patch("src.main.scrape_iris", return_value=[ITEM_IRIS])
    mocker.patch("src.main.scrape_kstartup", return_value=[ITEM_KSTARTUP])
    send_mock = mocker.patch("src.main.send_message")
    mocker.patch.dict(os.environ, ENV)
    await run()
    assert send_mock.call_count == 2


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
