from __future__ import annotations

from dataclasses import asdict
from datetime import datetime

from .models import AnalysisResult, Booking, ClientProfile, CustomerRequest


class ServioAdapter:
    """Maps Servio CRM/HMS-like dictionaries to internal module objects."""

    def client_from_servio(self, payload: dict) -> ClientProfile:
        bookings = [
            Booking(
                booking_id=str(item.get("booking_id", "")),
                room_type=str(item.get("room_type", "")),
                check_in=parse_datetime(item.get("check_in")),
                check_out=parse_datetime(item.get("check_out")),
                status=str(item.get("status", "")),
                total_amount=float(item.get("total_amount", 0)),
                paid_amount=float(item.get("paid_amount", 0)),
            )
            for item in payload.get("bookings", [])
        ]
        return ClientProfile(
            client_id=str(payload["client_id"]),
            full_name=str(payload.get("full_name", "Клієнт")),
            phone=payload.get("phone"),
            email=payload.get("email"),
            telegram_chat_id=payload.get("telegram_chat_id"),
            vip=bool(payload.get("vip", False)),
            blacklisted=bool(payload.get("blacklisted", False)),
            consent_to_marketing=bool(payload.get("consent_to_marketing", False)),
            preferences=list(payload.get("preferences", [])),
            bookings=bookings,
            complaints_count=int(payload.get("complaints_count", 0)),
            average_rating=payload.get("average_rating"),
            last_seen_at=parse_datetime(payload.get("last_seen_at")) if payload.get("last_seen_at") else None,
        )

    def request_from_servio(self, payload: dict) -> CustomerRequest:
        return CustomerRequest(
            request_id=str(payload["request_id"]),
            client_id=str(payload["client_id"]) if payload.get("client_id") else None,
            channel=str(payload.get("channel", "crm")),
            text=str(payload["text"]),
            created_at=parse_datetime(payload.get("created_at")),
            metadata=dict(payload.get("metadata", {})),
        )

    def result_to_servio_task(self, result: AnalysisResult) -> dict:
        data = asdict(result)
        data["category"] = result.category.value
        data["priority"] = result.priority.value
        return {
            "title": f"{result.category.value}: {result.priority.value}",
            "assigned_to": result.assign_to,
            "priority": result.priority.value,
            "description": "\n".join(result.recommended_actions),
            "tags": result.tags,
            "ai_analysis": data,
        }


def parse_datetime(value: object) -> datetime:
    if isinstance(value, datetime):
        return value
    if not value:
        return datetime.utcnow()
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
