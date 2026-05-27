from __future__ import annotations

from datetime import datetime, timedelta

from .models import ClientProfile, CustomerRequest


class BehaviorAnomalyDetector:
    """Scores unusual client behavior using transparent CRM features."""

    def score(self, request: CustomerRequest, client: ClientProfile | None) -> float:
        score = 0.0
        text = request.text.lower()

        if client is None:
            score += 0.15
        else:
            if client.blacklisted:
                score += 0.55
            if client.complaints_count >= 3:
                score += 0.2
            if client.average_rating is not None and client.average_rating <= 2.5:
                score += 0.15
            if self._is_long_absence(client.last_seen_at):
                score += 0.08

        if any(word in text for word in ("повернення коштів", "chargeback", "скасувати оплату")):
            score += 0.2
        if len(text) > 900:
            score += 0.08
        if request.channel.lower() in {"telegram", "facebook", "instagram"} and "http" in text:
            score += 0.12

        return round(min(score, 1.0), 3)

    @staticmethod
    def _is_long_absence(last_seen_at: datetime | None) -> bool:
        return last_seen_at is not None and datetime.utcnow() - last_seen_at > timedelta(days=365)
