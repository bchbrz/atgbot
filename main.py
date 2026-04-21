import asyncio
import logging
import os
import re

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.types import (
    MessageMediaDocument,
    MessageMediaPhoto,
    DocumentAttributeAudio,
    DocumentAttributeVideo,
)

BLOCKED_WORDS = ("trocus", "канал", "пост")
RUSSIAN_LETTERS_RE = re.compile(r"[А-Яа-яЁё]")


def env_required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Environment variable '{name}' is required")
    return value


def parse_chat_id(raw: str) -> int | str:
    raw = raw.strip()
    try:
        return int(raw)
    except ValueError:
        return raw


def is_allowed_message(message) -> bool:
    
    # Чистый текст без медиа.
    if message.media is None:
        return bool(message.message and message.message.strip())

    # Фото запрещаем сразу.
    if isinstance(message.media, MessageMediaPhoto):
        return False

    # Документы: пропускаем только стикеры.
    if isinstance(message.media, MessageMediaDocument):
        if message.sticker:
            return True

        # Дополнительная явная фильтрация медиа-атрибутов.
        doc = message.document
        if doc:
            for attr in doc.attributes:
                if isinstance(attr, (DocumentAttributeVideo, DocumentAttributeAudio)):
                    return False
        return False

    # Все остальные типы media блокируем.
    return False


async def main() -> None:
    load_dotenv()

    api_id = int(env_required("API_ID"))
    api_hash = env_required("API_HASH")
    source_chat = parse_chat_id(env_required("SOURCE_CHAT"))
    target_chat = parse_chat_id(env_required("TARGET_CHAT"))
    session_name = os.getenv("SESSION_NAME", "user_session")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    client = TelegramClient(session_name, api_id, api_hash)
    await client.start()
    me = await client.get_me()
    logging.info("Logged in as @%s (id=%s)", me.username, me.id)
    logging.info("Listening from %s and forwarding to %s", source_chat, target_chat)

    @client.on(events.NewMessage(pattern=r"^/start(?:@\w+)?$"))
    async def start_handler(event):
        if not event.is_private:
            return
        await event.respond("Работает")
        logging.info("Replied to /start from chat=%s", event.chat_id)

    @client.on(events.NewMessage(chats=source_chat))
    async def handler(event):
        message = event.message
        if message.message and message.message.strip().lower().startswith("/start"):
            logging.info("Skipped /start message id=%s", message.id)
            return

        text = (message.message or "").lower()
        if any(word in text for word in BLOCKED_WORDS):
            logging.info("Skipped message id=%s (contains blocked words)", message.id)
            return
        if RUSSIAN_LETTERS_RE.search(text):
            logging.info("Skipped message id=%s (contains russian text)", message.id)
            return

        if not is_allowed_message(message):
            logging.info("Skipped message id=%s (not text/sticker)", message.id)
            return

        try:
            await client.send_message(target_chat, message)
            logging.info("Forwarded message id=%s", message.id)
        except Exception as exc:
            logging.exception("Failed to send message id=%s: %s", message.id, exc)

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
