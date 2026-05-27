from __future__ import annotations

import re
from collections.abc import Iterable

from .models import RequestCategory, RequestPriority


NEGATIVE_WORDS = {
    "погано",
    "жах",
    "жахливо",
    "скарга",
    "проблема",
    "не працює",
    "брудно",
    "затримка",
    "скасувати",
    "повернення",
    "немає",
    "не задоволений",
}

POSITIVE_WORDS = {
    "дякую",
    "чудово",
    "добре",
    "сподобалось",
    "рекомендую",
    "комфортно",
    "приємно",
}

CATEGORY_KEYWORDS: dict[RequestCategory, set[str]] = {
    RequestCategory.BOOKING: {
        "бронювання",
        "забронювати",
        "номер",
        "заїзд",
        "виїзд",
        "дата",
        "проживання",
    },
    RequestCategory.PAYMENT: {
        "оплата",
        "рахунок",
        "чек",
        "повернення",
        "депозит",
        "картка",
        "борг",
    },
    RequestCategory.HOUSEKEEPING: {
        "прибирання",
        "рушник",
        "білизна",
        "брудно",
        "кондиціонер",
        "душ",
        "ремонт",
    },
    RequestCategory.FOOD: {
        "сніданок",
        "вечеря",
        "ресторан",
        "кава",
        "їжа",
        "напій",
        "меню",
    },
    RequestCategory.COMPLAINT: {
        "скарга",
        "незадоволений",
        "жахливо",
        "погано",
        "проблема",
        "адміністратор",
    },
    RequestCategory.LOYALTY: {
        "знижка",
        "бонус",
        "vip",
        "лояльність",
        "постійний",
    },
    RequestCategory.TRANSPORT: {
        "трансфер",
        "таксі",
        "аеропорт",
        "паркування",
        "авто",
    },
}


class RuleBasedRequestClassifier:
    """Fast deterministic classifier suitable for CRM event routing."""

    def classify(self, text: str) -> RequestCategory:
        normalized = normalize(text)
        scores: dict[RequestCategory, int] = {}

        for category, keywords in CATEGORY_KEYWORDS.items():
            scores[category] = sum(1 for word in keywords if word in normalized)

        best_category, best_score = max(scores.items(), key=lambda item: item[1])
        return best_category if best_score > 0 else RequestCategory.GENERAL

    def sentiment(self, text: str) -> float:
        normalized = normalize(text)
        negative = count_matches(normalized, NEGATIVE_WORDS)
        positive = count_matches(normalized, POSITIVE_WORDS)
        if positive == negative == 0:
            return 0.0
        raw_score = (positive - negative) / max(positive + negative, 1)
        return round(max(min(raw_score, 1.0), -1.0), 3)

    def priority(self, text: str, category: RequestCategory, sentiment_score: float) -> RequestPriority:
        normalized = normalize(text)
        urgent = any(word in normalized for word in ("терміново", "негайно", "зараз", "небезпека"))
        if "чорний список" in normalized or "поліція" in normalized or urgent and sentiment_score < -0.5:
            return RequestPriority.CRITICAL
        if category == RequestCategory.COMPLAINT or sentiment_score <= -0.5 or urgent:
            return RequestPriority.HIGH
        if category in {RequestCategory.PAYMENT, RequestCategory.BOOKING, RequestCategory.HOUSEKEEPING}:
            return RequestPriority.NORMAL
        return RequestPriority.LOW


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def count_matches(text: str, words: Iterable[str]) -> int:
    return sum(1 for word in words if word in text)
