from __future__ import annotations

from .models import ClientProfile, RequestCategory, RequestPriority


class ServiceRecommender:
    def recommend(
        self,
        category: RequestCategory,
        priority: RequestPriority,
        sentiment_score: float,
        anomaly_score: float,
        client: ClientProfile | None,
    ) -> list[str]:
        actions: list[str] = []

        if priority in {RequestPriority.HIGH, RequestPriority.CRITICAL}:
            actions.append("Передати звернення відповідальному менеджеру зміни.")
        if anomaly_score >= 0.5:
            actions.append("Перевірити історію гостя, платежі та попередні інциденти перед відповіддю.")

        category_actions = {
            RequestCategory.BOOKING: "Перевірити доступність номерів, статус бронювання та запропонувати актуальний тариф.",
            RequestCategory.PAYMENT: "Звірити оплату, баланс замовлення та сформувати рахунок або підтвердження платежу.",
            RequestCategory.HOUSEKEEPING: "Створити завдання службі housekeeping із дедлайном виконання.",
            RequestCategory.FOOD: "Передати запит у ресторанний модуль та врахувати харчові уподобання гостя.",
            RequestCategory.COMPLAINT: "Зафіксувати скаргу, вибачитися та запропонувати компенсаційну дію згідно з політикою готелю.",
            RequestCategory.LOYALTY: "Перевірити участь у програмі лояльності та доступні персональні пропозиції.",
            RequestCategory.TRANSPORT: "Уточнити час, місце подачі та передати заявку партнеру трансферу.",
            RequestCategory.GENERAL: "Уточнити потребу клієнта та прив'язати діалог до картки гостя.",
        }
        actions.append(category_actions[category])

        if client is not None:
            if client.vip:
                actions.append("Застосувати VIP-сценарій обслуговування та пріоритетну відповідь.")
            if client.preferences:
                actions.append("Врахувати вподобання гостя: " + ", ".join(client.preferences[:4]) + ".")
            if client.visits_count >= 3 and client.consent_to_marketing:
                actions.append("Запропонувати персональну акцію для постійного гостя.")

        if sentiment_score < -0.3:
            actions.append("Відповісти емпатично, без шаблонного тону, і підтвердити час вирішення.")

        return deduplicate(actions)

    def answer_template(
        self,
        category: RequestCategory,
        priority: RequestPriority,
        client: ClientProfile | None,
    ) -> str:
        name = client.full_name if client else "гостю"
        greeting = f"Добрий день, {name}!"
        if priority in {RequestPriority.HIGH, RequestPriority.CRITICAL}:
            return (
                f"{greeting} Дякуємо, що повідомили нас. Ваше звернення вже передано "
                "відповідальному співробітнику, ми повернемося з відповіддю найближчим часом."
            )
        if category == RequestCategory.BOOKING:
            return f"{greeting} Ми перевіримо доступність номерів і надішлемо вам найкращий варіант проживання."
        if category == RequestCategory.PAYMENT:
            return f"{greeting} Ми звіримо оплату за вашим замовленням і надішлемо підтвердження."
        return f"{greeting} Ваше звернення отримано та додано до CRM. Менеджер опрацює його найближчим часом."


def deduplicate(items: list[str]) -> list[str]:
    result: list[str] = []
    for item in items:
        if item not in result:
            result.append(item)
    return result
