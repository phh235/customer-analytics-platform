from __future__ import annotations

from customer_analytics.app.features.analytics.application.controlled_analytics_agent import (
    NO_POTENTIAL_SNAPSHOT_ANSWER,
    _empty_answer,
)
from customer_analytics.app.features.analytics.application.query_plan import (
    AnalyticsQueryPlan,
)
from customer_analytics.app.features.analytics.presentation.routes import (
    analytics_chat_routes,
)


def test_empty_potential_snapshot_has_freshness_aware_message() -> None:
    plan = AnalyticsQueryPlan(
        mode="rows",
        source="customer_potential_current",
    )

    assert _empty_answer(plan) == NO_POTENTIAL_SNAPSHOT_ANSWER


def test_unknown_analytics_response_is_user_facing_and_empty() -> None:
    response = analytics_chat_routes._unknown_analytics_response()

    assert response.answer == analytics_chat_routes.UNKNOWN_ANALYTICS_ANSWER
    assert response.data == []
    assert response.metadata.rows == 0
