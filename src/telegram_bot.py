import httpx


def format_announcement(announcement: dict) -> str:
    return (
        f"[{announcement['field']}] {announcement['title']}\n"
        f"기관: {announcement['inst']}\n"
        f"마감: {announcement.get('deadline', '미기재')}\n"
        f"{announcement['url']}"
    )


def split_messages(text: str, max_len: int = 4000) -> list[str]:
    return [text[i:i + max_len] for i in range(0, len(text), max_len)]


async def send_message(token: str, chat_id: str, text: str) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text},
        )
        response.raise_for_status()
