"""Intelligent CRM module for hotel customer service automation."""

from .models import (
    AnalysisResult,
    Booking,
    ClientProfile,
    CustomerRequest,
    RequestCategory,
    RequestPriority,
)
from .service import IntelligentCRMService

__all__ = [
    "AnalysisResult",
    "Booking",
    "ClientProfile",
    "CustomerRequest",
    "IntelligentCRMService",
    "RequestCategory",
    "RequestPriority",
]
