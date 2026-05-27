from __future__ import annotations

import json
from urllib import parse, request


class TelegramClient:
    """Minimal Telegram Bot API client for CRM notifications."""

    def __init__(self, bot_token: str | None, default_chat_id: str | None = None) -> None:
        self.bot_token = bot_token
        self.default_chat_id = default_chat_id

    def send_message(self, text: str, chat_id: str | None = None) -> dict:
        target_chat = chat_id or self.default_chat_id
        if not self.bot_token or not target_chat:
            return {"ok": False, "skipped": True, "reason": "telegram credentials are not configured"}

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        body = parse.urlencode({"chat_id": target_chat, "text": text}).encode("utf-8")
        req = request.Request(url, data=body, method="POST")
        with request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
