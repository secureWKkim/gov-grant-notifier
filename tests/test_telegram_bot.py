import pytest
from pytest_httpx import HTTPXMock

from src.telegram_bot import format_announcement, split_messages, send_message


SAMPLE = {
    "title": "2026년 스타트업 지원사업 공고",
    "inst": "중소벤처기업부 > 창업진흥원",
    "field": "사업화",
    "deadline": "2026-07-31",
    "url": "https://example.com/view?id=1",
}


# ── format_announcement ───────────────────────────────────────────────────────

def test_format_announcement_includes_title():
    assert SAMPLE["title"] in format_announcement(SAMPLE)


def test_format_announcement_includes_institution():
    assert SAMPLE["inst"] in format_announcement(SAMPLE)


def test_format_announcement_includes_field():
    assert SAMPLE["field"] in format_announcement(SAMPLE)


def test_format_announcement_includes_deadline():
    assert SAMPLE["deadline"] in format_announcement(SAMPLE)


def test_format_announcement_includes_url():
    assert SAMPLE["url"] in format_announcement(SAMPLE)


# ── split_messages ────────────────────────────────────────────────────────────

def test_split_messages_returns_single_chunk_when_text_fits():
    text = "짧은 메시지"
    parts = split_messages(text)
    assert parts == [text]


def test_split_messages_splits_8500_chars_into_three_chunks():
    parts = split_messages("가" * 8500)
    assert len(parts) == 3


def test_split_messages_each_chunk_is_at_most_4000_chars():
    parts = split_messages("x" * 12001)
    assert all(len(p) <= 4000 for p in parts)


def test_split_messages_preserves_all_content():
    text = "ab" * 3000
    assert "".join(split_messages(text)) == text


# ── send_message ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_send_message_posts_to_telegram_api(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url="https://api.telegram.org/botTEST_TOKEN/sendMessage",
        json={"ok": True, "result": {}},
    )
    await send_message(token="TEST_TOKEN", chat_id="123456", text="안녕하세요")
    assert len(httpx_mock.get_requests()) == 1


@pytest.mark.asyncio
async def test_send_message_sends_correct_chat_id(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url="https://api.telegram.org/botTEST_TOKEN/sendMessage",
        json={"ok": True, "result": {}},
    )
    await send_message(token="TEST_TOKEN", chat_id="123456", text="테스트")
    import json
    payload = json.loads(httpx_mock.get_requests()[0].read())
    assert payload["chat_id"] == "123456"


@pytest.mark.asyncio
async def test_send_message_sends_correct_text(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url="https://api.telegram.org/botTEST_TOKEN/sendMessage",
        json={"ok": True, "result": {}},
    )
    await send_message(token="TEST_TOKEN", chat_id="123456", text="테스트 메시지")
    import json
    payload = json.loads(httpx_mock.get_requests()[0].read())
    assert payload["text"] == "테스트 메시지"


@pytest.mark.asyncio
async def test_send_message_raises_on_http_error(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        method="POST",
        url="https://api.telegram.org/botTEST_TOKEN/sendMessage",
        status_code=400,
        json={"ok": False, "description": "Bad Request"},
    )
    with pytest.raises(Exception):
        await send_message(token="TEST_TOKEN", chat_id="123456", text="오류 테스트")
