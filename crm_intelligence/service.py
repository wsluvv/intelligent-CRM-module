from __future__ import annotations

from .anomaly import BehaviorAnomalyDetector
from .classifier import RuleBasedRequestClassifier
from .models import AnalysisResult, ClientProfile, CustomerRequest, RequestPriority
from .recommender import ServiceRecommender


class IntelligentCRMService:
    """Coordinates classification, risk scoring and service recommendations."""

    def __init__(
        self,
        classifier: RuleBasedRequestClassifier | None = None,
        anomaly_detector: BehaviorAnomalyDetector | None = None,
        recommender: ServiceRecommender | None = None,
    ) -> None:
        self.classifier = classifier or RuleBasedRequestClassifier()
        self.anomaly_detector = anomaly_detector or BehaviorAnomalyDetector()
        self.recommender = recommender or ServiceRecommender()

    def analyze(self, request: CustomerRequest, client: ClientProfile | None) -> AnalysisResult:
        category = self.classifier.classify(request.text)
        sentiment = self.classifier.sentiment(request.text)
        priority = self.classifier.priority(request.text, category, sentiment)
        anomaly_score = self.anomaly_detector.score(request, client)

        if anomaly_score >= 0.7 and priority != RequestPriority.CRITICAL:
            priority = RequestPriority.HIGH

        recommended_actions = self.recommender.recommend(
            category=category,
            priority=priority,
            sentiment_score=sentiment,
            anomaly_score=anomaly_score,
            client=client,
        )
        answer = self.recommender.answer_template(category, priority, client)

        return AnalysisResult(
            request_id=request.request_id,
            category=category,
            priority=priority,
            sentiment_score=sentiment,
            anomaly_score=anomaly_score,
            recommended_actions=recommended_actions,
            answer_template=answer,
            assign_to=self._assignee(priority, category.value),
            tags=self._tags(category.value, priority.value, anomaly_score, client),
        )

    @staticmethod
    def _assignee(priority: RequestPriority, category: str) -> str:
        if priority == RequestPriority.CRITICAL:
            return "hotel_manager"
        if priority == RequestPriority.HIGH:
            return "shift_supervisor"
        return {
            "booking": "reservation_department",
            "payment": "accounting_department",
            "housekeeping": "housekeeping_department",
            "food": "restaurant_department",
            "transport": "concierge",
        }.get(category, "reception")

    @staticmethod
    def _tags(category: str, priority: str, anomaly_score: float, client: ClientProfile | None) -> list[str]:
        tags = [category, priority]
        if anomaly_score >= 0.5:
            tags.append("risk-check")
        if client and client.vip:
            tags.append("vip")
        if client is None:
            tags.append("unidentified-client")
        return tags
