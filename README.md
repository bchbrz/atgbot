# Telegram Filter Reposter Bot

Бот читает новые посты из одного канала и отправляет в другой **только**:
- текстовые сообщения;
- стикеры.

Все остальные типы контента (фото, видео, GIF, документы, голосовые, кружки и т.д.) автоматически пропускаются.

## 1) Что нужно заранее

1. Python 3.10+.
2. Telegram `api_id` и `api_hash` с [my.telegram.org](https://my.telegram.org).
3. Аккаунт/бот должен иметь доступ к исходному каналу и право писать в целевой канал.

> В этом скрипте используется `Telethon` как пользовательский клиент (user session).

## 2) Установка

```powershell
cd C:\Users\antiv\telegram_filter_reposter_bot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3) Настройка

Скопируй `.env.example` в `.env` и заполни:

- `API_ID` — твой API ID;
- `API_HASH` — твой API HASH;
- `SOURCE_CHAT` — ID или username исходного канала;
- `TARGET_CHAT` — ID или username целевого канала;
- `SESSION_NAME` — имя файла сессии (можно оставить по умолчанию).

Пример:

```env
API_ID=12345678
API_HASH=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SOURCE_CHAT=-1001234567890
TARGET_CHAT=-1009876543210
SESSION_NAME=user_session
```

## 4) Запуск

```powershell
python main.py
```

При первом запуске Telethon попросит номер телефона и код подтверждения Telegram.

## 5) Важно по фильтрации

Скрипт пропускает:
- сообщения с `message.media is None` и непустым текстом;
- сообщения со стикером (`message.sticker`).

Блокирует:
- `photo`;
- любые документы, кроме стикеров;
- все остальные типы медиа.
