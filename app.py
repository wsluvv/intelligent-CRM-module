from __future__ import annotations

import os
from pathlib import Path

try:
    from fastapi import FastAPI
except ImportError:  # pragma: no cover
    FastAPI = None

from crm_intelligence.repository import JsonClientRepository
from crm_intelligence.service import IntelligentCRMService
from crm_intelligence.servio_adapter import ServioAdapter
from crm_intelligence.telegram_client import TelegramClient


if FastAPI is None:
    raise SystemExit("Install FastAPI to run the HTTP API: pip install fastapi uvicorn")


app = FastAPI(title="Hotel CRM Intelligent Module", version="1.0.0")
service = IntelligentCRMService()
adapter = ServioAdapter()
clients = JsonClientRepository(Path(__file__).parent / "data" / "clients.json")
telegram = TelegramClient(
    bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
    default_chat_id=os.getenv("TELEGRAM_ALERT_CHAT_ID"),
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "module": "hotel-crm-intelligence"}


@app.post("/analyze-request")
def analyze_request(payload: dict) -> dict:
    customer_request = adapter.request_from_servio(payload)
    client = clients.find_by_id(customer_request.client_id)
    result = service.analyze(customer_request, client)
    servio_task = adapter.result_to_servio_task(result)

    if result.priority.value in {"high", "critical"}:
        telegram.send_message(
            text=(
                f"CRM alert: {result.priority.value.upper()} / {result.category.value}\n"
                f"Request: {customer_request.text[:300]}\n"
                f"Assign to: {result.assign_to}"
            )
        )

    return {"analysis": servio_task["ai_analysis"], "servio_task": servio_task}
