"""API schema generation regression coverage."""

from __future__ import annotations

from customer_analytics.main import app


def test_openapi_generation_resolves_dependency_aliases() -> None:
    """OpenAPI generation resolves postponed FastAPI dependency annotations."""
    schema = app.openapi()

    assert "/api/v1/customers" in schema["paths"]
    assert "/api/v1/analytics/models" in schema["paths"]
    assert "/api/v1/analytics/dashboard/overview" in schema["paths"]
    assert "/api/v1/analytics/dashboard/options" in schema["paths"]
    assert "/api/v1/analytics/dashboard/export.csv" in schema["paths"]
    overview_parameters = {
        parameter["name"]
        for parameter in schema["paths"]["/api/v1/analytics/dashboard/overview"]["get"][
            "parameters"
        ]
    }
    assert {
        "opportunity_page",
        "opportunity_page_size",
        "priority_page",
        "priority_page_size",
    } <= overview_parameters
    segment_path = schema["paths"]["/api/v1/analytics/segments"]["get"]
    segment_parameters = {parameter["name"] for parameter in segment_path["parameters"]}
    assert {"page", "size"} <= segment_parameters
    assert (
        segment_path["responses"]["200"]["content"]["application/json"]["schema"][
            "$ref"
        ]
        == "#/components/schemas/PaginatedSegmentsResponse"
    )
    segment_properties = schema["components"]["schemas"]["SegmentResponse"][
        "properties"
    ]
    assert {
        "potential_score",
        "potential_level",
        "rfm",
        "score_components",
    } <= set(segment_properties)
    assert "403" in segment_path["responses"]
    for path in (
        "/api/v1/analytics/segments",
        "/api/v1/analytics/predictions/purchase-repeat",
        "/api/v1/analytics/priority-list",
    ):
        assert path in schema["paths"]
        parameters = {
            parameter["name"]
            for parameter in schema["paths"][path]["get"]["parameters"]
        }
        assert "search" in parameters
    assert "/api/v1/orders" in schema["paths"]
    order_parameters = {
        parameter["name"]
        for parameter in schema["paths"]["/api/v1/orders"]["get"]["parameters"]
    }
    assert "search" in order_parameters
    for path in (
        "/api/v1/auth/register",
        "/api/v1/auth/password/forgot/request",
        "/api/v1/auth/password/forgot/verify",
        "/api/v1/auth/password/reset",
    ):
        assert path in schema["paths"]
