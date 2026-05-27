from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class RequestCategory(str, Enum):
    BOOKING = "booking"
    PAYMENT = "payment"
    HOUSEKEEPING = "housekeeping"
    FOOD = "food"
    COMPLAINT = "complaint"
    LOYALTY = "loyalty"
    TRANSPORT = "transport"
    GENERAL = "general"


class RequestPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class Booking:
    booking_id: str
    room_type: str
    check_in: datetime
    check_out: datetime
    status: str
    total_amount: float
    paid_amount: float

    @property
    def debt(self) -> float:
        return max(self.total_amount - self.paid_amount, 0.0)


@dataclass(frozen=True)
class ClientProfile:
    client_id: str
    full_name: str
    phone: str | None = None
    email: str | None = None
    telegram_chat_id: str | None = None
    vip: bool = False
    blacklisted: bool = False
    consent_to_marketing: bool = False
    preferences: list[str] = field(default_factory=list)
    bookings: list[Booking] = field(default_factory=list)
    complaints_count: int = 0
    average_rating: float | None = None
    last_seen_at: datetime | None = None

    @property
    def visits_count(self) -> int:
        return len(self.bookings)

    @property
    def lifetime_value(self) -> float:
        return sum(booking.total_amount for booking in self.bookings)


@dataclass(frozen=True)
class CustomerRequest:
    request_id: str
    client_id: str | None
    channel: str
    text: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, str | int | float | bool] = field(default_factory=dict)


@dataclass(frozen=True)
class AnalysisResult:
    request_id: str
    category: RequestCategory
    priority: RequestPriority
    sentiment_score: float
    anomaly_score: float
    recommended_actions: list[str]
    answer_template: str
    assign_to: str
    tags: list[str]
