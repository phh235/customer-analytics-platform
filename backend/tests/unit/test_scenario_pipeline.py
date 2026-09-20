from datetime import date
from decimal import Decimal

import pytest

from customer_analytics.app.features.analytics.application.services.purchase_model import (  # noqa: E501
    predict_purchase_probability,
    train_purchase_model,
)
from customer_analytics.app.features.analytics.domain.enums import ScoreLevel
from customer_analytics.app.features.analytics.infrastructure.repositories.analytics_repository_impl import (  # noqa: E501
    AnalyticsRepositoryImpl,
)
from customer_analytics.app.features.import_data.application.services.data_quality_service import (  # noqa: E501
    validate_import_data,
)
from customer_analytics.app.features.import_data.application.services.file_parser import (  # noqa: E501
    suggest_mapping,
)


def test_interaction_import_mapping_and_validation_accept_delivered_orders() -> None:
    mapping = suggest_mapping(
        [
            "interaction_id",
            "customer_id",
            "product_id",
            "interaction_type",
            "interaction_timestamp",
        ],
        "INTERACTION",
    )
    assert mapping["interaction_timestamp"] == "interaction_timestamp"
    errors = validate_import_data(
        [
            {
                "order_id": "DH00059",
                "customer_id": "KH0013",
                "order_date": "2026-08-20",
                "total_amount": "100000",
                "status": "delivered",
            }
        ],
        "ORDER",
    )
    assert errors == []


def test_logistic_purchase_model_exposes_scenario_metrics_and_probability() -> None:
    rows = [
        {
            "label": index % 2,
            "recency": 5 if index % 2 else 80,
            "frequency": 8 if index % 2 else 1,
            "monetary": 18000000 if index % 2 else 500000,
            "aov": 2250000 if index % 2 else 500000,
            "purchase_cycle": 34 if index % 2 else 120,
            "interaction_score": 76 if index % 2 else 5,
            "product_diversity": 4 if index % 2 else 1,
            "review_score": 4.8 if index % 2 else 2.0,
        }
        for index in range(8)
    ]
    artifact, metrics = train_purchase_model(rows, "LOGISTIC_REGRESSION")
    assert {
        "accuracy",
        "precision",
        "recall",
        "f1_score",
        "roc_auc",
        "pr_auc",
        "lift_top10",
    } <= metrics.keys()
    probability = predict_purchase_probability(artifact, rows[1])
    assert 0 <= probability <= 1

async def test_script_duan_potential_score_uses_excel_component_formula() -> None:
    repository = AnalyticsRepositoryImpl(None)  # type: ignore[arg-type]
    scores = await repository.get_all_potential_scores(
        days=365,
        analysis_date=date(2026, 9, 1),
        rows=[
            {
                "customer_id": "KH0001",
                "name": "KH0001",
                "recency_days": 5,
                "frequency": 10,
                "monetary": Decimal("20000000"),
                "first_purchase_date": None,
                "recent_spend": Decimal("20000000"),
                "previous_spend": Decimal("0"),
                "interaction_score": Decimal("80"),
            },
            {
                "customer_id": "KH0013",
                "name": "KH0013",
                "recency_days": 12,
                "frequency": 8,
                "monetary": Decimal("18500000"),
                "first_purchase_date": None,
                "recent_spend": Decimal("18500000"),
                "previous_spend": Decimal("0"),
                "interaction_score": Decimal("76"),
            },
            {
                "customer_id": "KH0002",
                "name": "KH0002",
                "recency_days": 20,
                "frequency": 7,
                "monetary": Decimal("15000000"),
                "first_purchase_date": None,
                "recent_spend": Decimal("15000000"),
                "previous_spend": Decimal("0"),
                "interaction_score": Decimal("60"),
            },
            {
                "customer_id": "KH0003",
                "name": "KH0003",
                "recency_days": 30,
                "frequency": 4,
                "monetary": Decimal("5000000"),
                "first_purchase_date": None,
                "recent_spend": Decimal("5000000"),
                "previous_spend": Decimal("0"),
                "interaction_score": Decimal("40"),
            },
            {
                "customer_id": "KH0004",
                "name": "KH0004",
                "recency_days": 40,
                "frequency": 2,
                "monetary": Decimal("1000000"),
                "first_purchase_date": None,
                "recent_spend": Decimal("1000000"),
                "previous_spend": Decimal("0"),
                "interaction_score": Decimal("5"),
            },
        ],
    )

    target = next(score for score in scores if score.customer_id == "KH0013")
    assert target.score == 82.36
    assert target.level is ScoreLevel.HIGH
    assert target.components["recency"] == 4
    assert target.components["frequency"] == 4
    assert target.components["monetary"] == 4
    assert target.components["interaction"] == pytest.approx(4.7866667)
    assert target.components["interactionRaw"] == 76

def test_frequency_percentile_includes_zero_order_customers() -> None:
    repository = AnalyticsRepositoryImpl(None)  # type: ignore[arg-type]
    rows = [
        {"customer_id": f"customer-{frequency}", "frequency": frequency}
        for frequency in (0, 1, 2, 3, 9)
    ]

    scores = repository._percentile_scores(
        rows,
        lambda row: float(row["frequency"]),
        higher_is_better=True,
    )

    assert scores["customer-3"] == 4

async def test_insufficient_data_preserves_null_scores() -> None:
    repository = AnalyticsRepositoryImpl(None)  # type: ignore[arg-type]
    scores = await repository.get_all_potential_scores(
        days=365,
        analysis_date=date(2026, 9, 1),
        rows=[
            {
                "customer_id": "customer-without-orders",
                "name": "No Orders",
                "recency_days": None,
                "frequency": 0,
                "monetary": Decimal("0"),
                "first_purchase_date": None,
                "recent_spend": Decimal("0"),
                "previous_spend": Decimal("0"),
                "interaction_score": Decimal("20"),
            }
        ],
    )

    assert len(scores) == 1
    assert scores[0].score is None
    assert scores[0].level is ScoreLevel.INSUFFICIENT_DATA
    assert scores[0].components["missingComponents"] == [
        "recency",
        "frequency",
        "monetary",
    ]


class _AnalysisDateResult:
    def mappings(self) -> "_AnalysisDateResult":
        return self

    def first(self) -> dict[str, date]:
        return {"analysis_date": date(2026, 8, 13)}


class _AnalysisDateSession:
    async def execute(self, _query: object) -> _AnalysisDateResult:
        return _AnalysisDateResult()


async def test_latest_analysis_date_reads_completed_snapshot_date() -> None:
    repository = AnalyticsRepositoryImpl(_AnalysisDateSession())  # type: ignore[arg-type]

    assert await repository.get_latest_analysis_date() == date(2026, 8, 13)
