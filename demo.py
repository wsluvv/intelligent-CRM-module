from __future__ import annotations

import json
from pathlib import Path

from crm_intelligence.repository import JsonClientRepository
from crm_intelligence.service import IntelligentCRMService
from crm_intelligence.servio_adapter import ServioAdapter


ROOT = Path(__file__).parent


def main() -> None:
    adapter = ServioAdapter()
    service = IntelligentCRMService()
    clients = JsonClientRepository(ROOT / "data" / "clients.json")

    payload = {
        "request_id": "REQ-1007",
        "client_id": "G-001",
        "channel": "telegram",
        "text": "Терміново! У номері брудно, не працює кондиціонер і я дуже незадоволений сервісом.",
        "created_at": "2026-05-27T15:40:00",
    }

    request = adapter.request_from_servio(payload)
    client = clients.find_by_id(request.client_id)
    result = service.analyze(request, client)
    print(json.dumps(adapter.result_to_servio_task(result), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
