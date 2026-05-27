from __future__ import annotations

import json
from pathlib import Path

from .models import ClientProfile
from .servio_adapter import ServioAdapter


class JsonClientRepository:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.adapter = ServioAdapter()

    def find_by_id(self, client_id: str | None) -> ClientProfile | None:
        if not client_id or not self.path.exists():
            return None

        data = json.loads(self.path.read_text(encoding="utf-8"))
        for item in data:
            if str(item.get("client_id")) == str(client_id):
                return self.adapter.client_from_servio(item)
        return None
