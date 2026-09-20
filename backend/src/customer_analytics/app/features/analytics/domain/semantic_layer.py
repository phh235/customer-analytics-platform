"""Controlled business vocabulary exposed to the analytics agent."""

from __future__ import annotations

ANALYTICS_SCHEMA = "analytics"

ANALYTICS_VIEWS: dict[str, dict[str, str]] = {
    "customer_sales": {
        "created_at": "Order creation timestamp",
        "total_amount": "Gross order amount",
        "net_amount": "Order amount after refund",
        "status": "Order status",
        "customer_region": "Customer region",
    },
    "product_sales": {
        "product_name": "Product display name",
        "category": "Product category",
        "created_at": "Order creation timestamp",
        "quantity": "Quantity sold",
        "line_total": "Order-line total amount",
        "status": "Order status",
    },
}
ADMIN_RAW_TABLES: dict[str, frozenset[str]] = {
    "customers": frozenset(
        {
            "id",
            "name",
            "email",
            "phone",
            "address",
            "status",
            "region",
            "customer_since",
            "customer_code",
            "source_customer_id",
            "zip_code",
            "city",
            "state_code",
            "province_city",
            "registered_at",
            "owner_id",
            "is_deleted",
            "created_at",
            "updated_at",
        }
    ),
    "orders": frozenset(
        {
            "id",
            "customer_id",
            "order_number",
            "order_date",
            "total_amount",
            "refund_amount",
            "net_amount",
            "status",
            "channel",
            "notes",
            "created_at",
            "updated_at",
        }
    ),
    "order_items": frozenset(
        {
            "id",
            "order_id",
            "product_id",
            "quantity",
            "unit_price",
            "subtotal",
            "line_subtotal",
            "line_amount",
            "line_total",
        }
    ),
    "products": frozenset(
        {
            "id",
            "source_product_id",
            "product_code",
            "sku",
            "name",
            "category",
            "source_category_code",
            "description",
            "image_url",
            "price",
            "list_price",
            "currency",
            "status",
            "is_deleted",
            "created_at",
            "updated_at",
        }
    ),
}
ADMIN_RAW_TABLE_DESCRIPTIONS: dict[str, str] = {
    "customers": "Customer master records. PII fields are ADMIN-only.",
    "orders": "Order headers with customer, date, status, and money fields.",
    "order_items": "Order lines linking orders to products and quantities.",
    "products": "Product catalog records and categories.",
}

ANALYTICS_RELATIONSHIPS = (
    "analytics.customer_sales joins orders to customers and excludes "
    "deleted customers.",
    "analytics.product_sales joins order_items to orders and products "
    "and excludes deleted products.",
    "public.orders.customer_id joins public.customers.id.",
    "public.order_items.order_id joins public.orders.id.",
    "public.order_items.product_id joins public.products.id.",
)

ANALYTICS_DIMENSIONS: dict[str, dict[str, str]] = {
    "customer_region": {
        "source": "customer_sales",
        "expression": "customer_region",
        "description": "Customer region",
    },
    "product_name": {
        "source": "product_sales",
        "expression": "product_name",
        "description": "Product display name",
    },
    "category": {
        "source": "product_sales",
        "expression": "category",
        "description": "Product category",
    },
}


ANALYTICS_TIME_BUCKETS = {
    "day": "day",
    "week": "week",
    "month": "month",
    "quarter": "quarter",
    "year": "year",
}


ANALYTICS_METRIC_SOURCES = {
    "order_count": "customer_sales",
    "revenue": "customer_sales",
    "gross_revenue": "customer_sales",
    "average_order_value": "customer_sales",
    "quantity_sold": "product_sales",
}


ANALYTICS_METRIC_EXPRESSIONS = {
    "order_count": "COUNT(*)",
    "revenue": "COALESCE(SUM(net_amount), 0)",
    "gross_revenue": "COALESCE(SUM(total_amount), 0)",
    "average_order_value": (
        "COALESCE(SUM(net_amount), 0) / NULLIF(COUNT(*), 0)"
    ),
    "quantity_sold": "COALESCE(SUM(quantity), 0)",
}


ANALYTICS_METRICS = {
    "order_count": "Number of delivered orders",
    "revenue": "Net revenue (SUM(net_amount)) from delivered orders",
    "gross_revenue": "Gross revenue (SUM(total_amount)) from delivered orders",
    "average_order_value": "Net revenue divided by delivered order count",
    "quantity_sold": "Quantity sold on delivered order lines",
}


ALLOWED_RESULT_ALIASES = frozenset(
    {
        "order_count",
        "revenue",
        "gross_revenue",
        "average_order_value",
        "quantity_sold",
        "period",
    }
)




def build_schema_context(*, admin_mode: bool = False) -> str:
    """Render the schema context sent to the analytics planner."""
    view_lines = []
    for view_name, columns in ANALYTICS_VIEWS.items():
        view_lines.append(f"analytics.{view_name}")
        view_lines.extend(
            f"- {name}: {description}" for name, description in columns.items()
        )

    metric_lines = [
        f"- {name}: {description}" for name, description in ANALYTICS_METRICS.items()
    ]
    lines = [
        "Available analytics views:",
        *view_lines,
        "",
        "Business metrics:",
        *metric_lines,
        "",
        "Supported dimensions:",
        *(
            f"- {name}: {details['description']} "
            f"(source: analytics.{details['source']})"
            for name, details in ANALYTICS_DIMENSIONS.items()
        ),
        "",
        "Relationships:",
        *(f"- {relationship}" for relationship in ANALYTICS_RELATIONSHIPS),
        "",
        "Planner contract:",
        '- Return JSON with mode "aggregate" or "rows".',
        '- For aggregates, provide metric, date_from/date_to as ISO dates, '
        "optional group_by and time_bucket.",
        '- For row listings, provide source and columns; ADMIN may use "*" '
        "for approved raw tables.",
        "- Use half-open date ranges: date >= date_from and date < date_to.",
        "- Use status = 'delivered' for business metrics.",
        "- Return at most 100 rows.",
    ]
    if admin_mode:
        lines.extend(
            [
                "",
                "ADMIN raw tables:",
                *(
                    f"- public.{name}: {description} "
                    f"columns={sorted(ADMIN_RAW_TABLES[name])}"
                    for name, description in ADMIN_RAW_TABLE_DESCRIPTIONS.items()
                ),
                "ADMIN mode may use explicit public tables and SELECT *.",
            ]
        )
    else:
        lines.extend(
            [
                "- Use analytics schema only.",
                "- Never select PII such as email, phone, address, or credentials.",
                "- Never access base tables.",
            ]
        )
    return "\n".join(lines)
