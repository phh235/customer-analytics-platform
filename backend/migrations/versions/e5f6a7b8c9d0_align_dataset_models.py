"""Align database models with the dataset inventory and SRS contract.

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
"""

from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision: str = "e5f6a7b8c9d0"
down_revision: str | Sequence[str] | None = "d4e5f6a7b8c9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create aligned source, configuration, history, and audit tables."""
    op.create_table(
        "employees",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("employee_code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("region_scope", sa.String(100), nullable=True),
        sa.Column("status", sa.String(20), server_default="ACTIVE", nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_employees"),
        sa.UniqueConstraint("employee_code", name="uq_employees_employee_code"),
        sa.UniqueConstraint("email", name="uq_employees_email"),
    )
    op.create_index("ix_employees_status", "employees", ["status"])

    op.create_table(
        "sellers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("seller_code", sa.String(50), nullable=False),
        sa.Column("seller_name", sa.String(150), nullable=True),
        sa.Column("zip_code", sa.String(20), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state_code", sa.String(20), nullable=True),
        sa.Column("region", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_sellers"),
        sa.UniqueConstraint("seller_code", name="uq_sellers_seller_code"),
    )

    op.create_table(
        "geolocations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("zip_code", sa.String(20), nullable=False),
        sa.Column("latitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("longitude", sa.Numeric(10, 7), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state_code", sa.String(20), nullable=True),
        sa.Column("region", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_geolocations"),
        sa.UniqueConstraint("zip_code", name="uq_geolocations_zip_code"),
    )

    op.create_table(
        "campaigns",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("campaign_code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("campaign_type", sa.String(50), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("channel", sa.String(50), nullable=True),
        sa.Column("target_segment", sa.String(100), nullable=True),
        sa.Column("status", sa.String(20), server_default="ACTIVE", nullable=False),
        sa.Column("budget_vnd", sa.Numeric(14, 2), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_campaigns"),
        sa.UniqueConstraint("campaign_code", name="uq_campaigns_campaign_code"),
    )

    op.create_table(
        "payments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("payment_sequence", sa.Integer(), nullable=False),
        sa.Column("payment_type", sa.String(50), nullable=True),
        sa.Column("payment_method", sa.String(50), nullable=True),
        sa.Column("payment_installments", sa.Integer(), nullable=True),
        sa.Column("payment_value", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="VND", nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_payments"),
        sa.UniqueConstraint(
            "order_id", "payment_sequence", name="uq_payments_order_sequence"
        ),
    )
    op.create_index("ix_payments_order_id", "payments", ["order_id"])

    op.create_table(
        "reviews",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("review_code", sa.String(50), nullable=True),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("channel", sa.String(50), nullable=True),
        sa.Column("review_created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_reviews"),
        sa.UniqueConstraint("review_code", name="uq_reviews_review_code"),
        sa.CheckConstraint("score BETWEEN 1 AND 5", name="ck_reviews_score_range"),
    )
    op.create_index("ix_reviews_order_id", "reviews", ["order_id"])
    op.create_index("ix_reviews_customer_id", "reviews", ["customer_id"])

    op.create_table(
        "customer_interactions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("interaction_code", sa.String(100), nullable=True),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("campaign_id", sa.Uuid(), nullable=True),
        sa.Column("interaction_type", sa.String(50), nullable=False),
        sa.Column("interaction_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("channel", sa.String(50), nullable=True),
        sa.Column("session_id", sa.String(100), nullable=True),
        sa.Column(
            "interaction_value", sa.Numeric(10, 4), server_default="0", nullable=False
        ),
        sa.Column("interaction_result", sa.String(100), nullable=True),
        sa.Column(
            "is_mock_data", sa.Boolean(), server_default=sa.true(), nullable=False
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_customer_interactions"),
        sa.UniqueConstraint(
            "interaction_code", name="uq_customer_interactions_interaction_code"
        ),
    )
    op.create_index(
        "ix_customer_interactions_customer_id", "customer_interactions", ["customer_id"]
    )
    op.create_index(
        "ix_customer_interactions_product_id", "customer_interactions", ["product_id"]
    )
    op.create_index(
        "ix_customer_interactions_campaign_id", "customer_interactions", ["campaign_id"]
    )
    op.create_index(
        "ix_customer_interactions_timestamp",
        "customer_interactions",
        ["interaction_timestamp"],
    )

    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_id", name="pk_user_roles"),
    )
    op.execute(
        sa.text(
            "INSERT INTO user_roles (user_id, role_id) SELECT id, role_id FROM users"
        )
    )

    op.create_table(
        "customer_assignments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("assigned_by", sa.Uuid(), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.ForeignKeyConstraint(["assigned_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_customer_assignments"),
    )
    op.create_index(
        "ix_customer_assignments_customer_id", "customer_assignments", ["customer_id"]
    )
    op.create_index(
        "ix_customer_assignments_user_id", "customer_assignments", ["user_id"]
    )

    op.create_table(
        "configuration_versions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("version", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), server_default="ACTIVE", nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("effective_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_configuration_versions"),
        sa.UniqueConstraint("version", name="uq_configuration_versions_version"),
    )

    op.create_table(
        "scoring_rules",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("configuration_version_id", sa.Uuid(), nullable=False),
        sa.Column("component", sa.String(50), nullable=False),
        sa.Column("weight", sa.Numeric(6, 4), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.ForeignKeyConstraint(
            ["configuration_version_id"],
            ["configuration_versions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_scoring_rules"),
        sa.UniqueConstraint(
            "configuration_version_id",
            "component",
            name="uq_scoring_rules_version_component",
        ),
    )

    op.create_table(
        "scoring_thresholds",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("configuration_version_id", sa.Uuid(), nullable=False),
        sa.Column("component", sa.String(50), nullable=False),
        sa.Column("min_value", sa.Numeric(12, 4), nullable=True),
        sa.Column("max_value", sa.Numeric(12, 4), nullable=True),
        sa.Column("score", sa.Numeric(6, 2), nullable=False),
        sa.Column("priority", sa.Integer(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(
            ["configuration_version_id"],
            ["configuration_versions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_scoring_thresholds"),
    )

    op.create_table(
        "segmentation_rules",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("configuration_version_id", sa.Uuid(), nullable=False),
        sa.Column("segment_code", sa.String(50), nullable=False),
        sa.Column("min_potential_score", sa.Numeric(6, 2), nullable=True),
        sa.Column("max_potential_score", sa.Numeric(6, 2), nullable=True),
        sa.Column("priority", sa.Integer(), server_default="0", nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.ForeignKeyConstraint(
            ["configuration_version_id"],
            ["configuration_versions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_segmentation_rules"),
    )

    op.create_table(
        "valid_order_status_configs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("configuration_version_id", sa.Uuid(), nullable=False),
        sa.Column("order_status", sa.String(30), nullable=False),
        sa.Column("is_valid_for_analytics", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["configuration_version_id"],
            ["configuration_versions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_valid_order_status_configs"),
        sa.UniqueConstraint(
            "configuration_version_id",
            "order_status",
            name="uq_valid_order_status_config_version_status",
        ),
    )

    op.create_table(
        "analysis_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("run_code", sa.String(100), nullable=False),
        sa.Column("analysis_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), server_default="PENDING", nullable=False),
        sa.Column("analysis_date", sa.Date(), nullable=False),
        sa.Column("data_from", sa.Date(), nullable=True),
        sa.Column("data_to", sa.Date(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("executed_by", sa.Uuid(), nullable=True),
        sa.Column("configuration_version_id", sa.Uuid(), nullable=True),
        sa.Column("model_version_id", sa.Uuid(), nullable=True),
        sa.Column("total_records", sa.Integer(), server_default="0", nullable=False),
        sa.Column("success_records", sa.Integer(), server_default="0", nullable=False),
        sa.Column("failed_records", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["configuration_version_id"],
            ["configuration_versions.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(["executed_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["model_version_id"], ["model_registry.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_analysis_runs"),
        sa.UniqueConstraint("run_code", name="uq_analysis_runs_run_code"),
    )

    op.create_table(
        "customer_behavior_history",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("analysis_run_id", sa.Uuid(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("recency_days", sa.Integer(), nullable=False),
        sa.Column("frequency", sa.Integer(), nullable=False),
        sa.Column("monetary", sa.Numeric(12, 2), nullable=False),
        sa.Column("aov", sa.Numeric(12, 2), nullable=False),
        sa.Column("avg_purchase_cycle_days", sa.Numeric(12, 2), nullable=True),
        sa.Column("trend", sa.String(30), nullable=True),
        sa.Column("avg_review_score", sa.Numeric(5, 2), nullable=True),
        sa.ForeignKeyConstraint(
            ["analysis_run_id"], ["analysis_runs.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_customer_behavior_history"),
    )

    op.create_table(
        "customer_potential_score_history",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("analysis_run_id", sa.Uuid(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("r_score", sa.Numeric(6, 2), nullable=False),
        sa.Column("f_score", sa.Numeric(6, 2), nullable=False),
        sa.Column("m_score", sa.Numeric(6, 2), nullable=False),
        sa.Column(
            "interaction_score", sa.Numeric(6, 2), server_default="0", nullable=False
        ),
        sa.Column("potential_score", sa.Numeric(6, 2), nullable=False),
        sa.Column("potential_level", sa.String(30), nullable=False),
        sa.Column("configuration_version_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["analysis_run_id"], ["analysis_runs.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["configuration_version_id"],
            ["configuration_versions.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_customer_potential_score_history"),
    )

    op.create_table(
        "customer_product_preferences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("analysis_run_id", sa.Uuid(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("product_category_id", sa.Uuid(), nullable=True),
        sa.Column("product_category_name", sa.String(100), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("score", sa.Numeric(12, 4), nullable=False),
        sa.Column(
            "purchase_frequency", sa.Integer(), server_default="0", nullable=False
        ),
        sa.Column("quantity", sa.Integer(), server_default="0", nullable=False),
        sa.Column("monetary", sa.Numeric(12, 2), nullable=False),
        sa.Column("purchase_share", sa.Numeric(8, 5), nullable=False),
        sa.Column("last_purchase_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["analysis_run_id"], ["analysis_runs.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["product_category_id"], ["products.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_customer_product_preferences"),
    )

    op.create_table(
        "ml_model_evaluations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("model_version_id", sa.Uuid(), nullable=False),
        sa.Column("evaluation_dataset_version", sa.String(100), nullable=True),
        sa.Column("precision", sa.Numeric(10, 6), nullable=True),
        sa.Column("recall", sa.Numeric(10, 6), nullable=True),
        sa.Column("f1_score", sa.Numeric(10, 6), nullable=True),
        sa.Column("roc_auc", sa.Numeric(10, 6), nullable=True),
        sa.Column("pr_auc", sa.Numeric(10, 6), nullable=True),
        sa.Column("precision_at_k", sa.Numeric(10, 6), nullable=True),
        sa.Column("recall_at_k", sa.Numeric(10, 6), nullable=True),
        sa.Column("lift_at_k", sa.Numeric(10, 6), nullable=True),
        sa.Column("metrics", sa.JSON(), nullable=True),
        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["model_version_id"], ["model_registry.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_ml_model_evaluations"),
    )

    op.create_table(
        "import_errors",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("import_job_id", sa.Uuid(), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("field_name", sa.String(100), nullable=True),
        sa.Column("error_code", sa.String(100), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("raw_value", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["import_job_id"], ["import_jobs.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_import_errors"),
    )
    op.create_index(
        "ix_import_errors_import_job_id", "import_errors", ["import_job_id"]
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("actor_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("entity_id", sa.String(100), nullable=True),
        sa.Column("before_data", sa.JSON(), nullable=True),
        sa.Column("after_data", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_audit_logs"),
    )
    op.create_index("ix_audit_logs_actor_id", "audit_logs", ["actor_id"])
    op.create_index("ix_audit_logs_entity", "audit_logs", ["entity_type", "entity_id"])

    op.add_column("users", sa.Column("employee_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_users_employee_id_employees",
        "users",
        "employees",
        ["employee_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_users_employee_id", "users", ["employee_id"])

    customer_columns = [
        sa.Column("customer_code", sa.String(50), nullable=True),
        sa.Column("source_customer_id", sa.String(100), nullable=True),
        sa.Column("zip_code", sa.String(20), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state_code", sa.String(20), nullable=True),
        sa.Column("province_city", sa.String(150), nullable=True),
        sa.Column("registered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("owner_id", sa.Uuid(), nullable=True),
    ]
    for column in customer_columns:
        op.add_column("customers", column)
    op.create_foreign_key(
        "fk_customers_owner_id_employees",
        "customers",
        "employees",
        ["owner_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_customers_customer_code", "customers", ["customer_code"], unique=True
    )
    op.create_index(
        "ix_customers_source_customer_id",
        "customers",
        ["source_customer_id"],
        unique=True,
    )
    op.create_index("ix_customers_owner_id", "customers", ["owner_id"])

    product_columns = [
        sa.Column("source_product_id", sa.String(100), nullable=True),
        sa.Column("product_code", sa.String(64), nullable=True),
        sa.Column("source_category_code", sa.String(100), nullable=True),
        sa.Column("list_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("currency", sa.String(3), server_default="VND", nullable=False),
        sa.Column("weight_g", sa.Numeric(12, 3), nullable=True),
        sa.Column("length_cm", sa.Numeric(10, 3), nullable=True),
        sa.Column("height_cm", sa.Numeric(10, 3), nullable=True),
        sa.Column("width_cm", sa.Numeric(10, 3), nullable=True),
        sa.Column("photo_count", sa.Integer(), nullable=True),
        sa.Column(
            "is_deleted", sa.Boolean(), server_default=sa.false(), nullable=False
        ),
    ]
    for column in product_columns:
        op.add_column("products", column)
    op.create_index(
        "ix_products_source_product_id", "products", ["source_product_id"], unique=True
    )
    op.create_index(
        "ix_products_product_code", "products", ["product_code"], unique=True
    )
    op.create_index(
        "ix_products_source_category_code", "products", ["source_category_code"]
    )

    order_columns = [
        sa.Column("owner_id", sa.Uuid(), nullable=True),
        sa.Column("source_order_id", sa.String(100), nullable=True),
        sa.Column("order_code", sa.String(100), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_carrier_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_customer_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("estimated_delivery_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=True),
        sa.Column("freight_total", sa.Numeric(12, 2), nullable=True),
        sa.Column("discount_total", sa.Numeric(12, 2), nullable=True),
        sa.Column("payment_method", sa.String(50), nullable=True),
        sa.Column("sales_channel", sa.String(50), nullable=True),
        sa.Column("region", sa.String(100), nullable=True),
        sa.Column("province_city", sa.String(150), nullable=True),
        sa.Column("currency", sa.String(3), server_default="VND", nullable=False),
        sa.Column(
            "is_valid_for_rfm", sa.Boolean(), server_default=sa.true(), nullable=False
        ),
    ]
    for column in order_columns:
        op.add_column("orders", column)
    op.create_foreign_key(
        "fk_orders_owner_id_employees",
        "orders",
        "employees",
        ["owner_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_orders_owner_id", "orders", ["owner_id"])
    op.create_index(
        "ix_orders_source_order_id", "orders", ["source_order_id"], unique=True
    )
    op.create_index("ix_orders_order_code", "orders", ["order_code"], unique=True)

    item_columns = [
        sa.Column("seller_id", sa.Uuid(), nullable=True),
        sa.Column("item_sequence", sa.Integer(), nullable=True),
        sa.Column("freight_value", sa.Numeric(10, 2), nullable=True),
        sa.Column("discount_value", sa.Numeric(10, 2), nullable=True),
        sa.Column("line_subtotal", sa.Numeric(12, 2), nullable=True),
        sa.Column("line_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("line_total", sa.Numeric(12, 2), nullable=True),
        sa.Column("shipping_limit_at", sa.DateTime(timezone=True), nullable=True),
    ]
    for column in item_columns:
        op.add_column("order_items", column)
    op.create_foreign_key(
        "fk_order_items_seller_id_sellers",
        "order_items",
        "sellers",
        ["seller_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_order_items_seller_id", "order_items", ["seller_id"])

    registry_columns = [
        sa.Column(
            "model_code",
            sa.String(100),
            server_default="PURCHASE_REPEAT",
            nullable=False,
        ),
        sa.Column("model_type", sa.String(100), nullable=True),
        sa.Column("dataset_version", sa.String(100), nullable=True),
        sa.Column("trained_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("feature_window_days", sa.Integer(), nullable=True),
        sa.Column("prediction_horizon_days", sa.Integer(), nullable=True),
        sa.Column("precision", sa.Numeric(10, 6), nullable=True),
        sa.Column("recall", sa.Numeric(10, 6), nullable=True),
        sa.Column("f1_score", sa.Numeric(10, 6), nullable=True),
        sa.Column("roc_auc", sa.Numeric(10, 6), nullable=True),
        sa.Column("notes", sa.String(1000), nullable=True),
    ]
    for column in registry_columns:
        op.add_column("model_registry", column)
    op.create_index("ix_model_registry_model_code", "model_registry", ["model_code"])

    op.add_column(
        "segment_history", sa.Column("analysis_run_id", sa.Uuid(), nullable=True)
    )
    op.add_column(
        "segment_history", sa.Column("segment_code", sa.String(50), nullable=True)
    )
    op.add_column(
        "segment_history", sa.Column("segment_name", sa.String(100), nullable=True)
    )
    op.add_column(
        "segment_history",
        sa.Column("configuration_version_id", sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        "fk_segment_history_analysis_run_id_analysis_runs",
        "segment_history",
        "analysis_runs",
        ["analysis_run_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_segment_history_customer_id_customers",
        "segment_history",
        "customers",
        ["customer_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_segment_history_config_version_id",
        "segment_history",
        "configuration_versions",
        ["configuration_version_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_segment_history_analysis_run_id", "segment_history", ["analysis_run_id"]
    )
    op.create_index(
        "ix_segment_history_configuration_version_id",
        "segment_history",
        ["configuration_version_id"],
    )

    prediction_columns = [
        sa.Column("analysis_run_id", sa.Uuid(), nullable=True),
        sa.Column("model_version_id", sa.Uuid(), nullable=True),
        sa.Column("feature_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("feature_to", sa.DateTime(timezone=True), nullable=True),
    ]
    for column in prediction_columns:
        op.add_column("purchase_predictions", column)
    op.create_foreign_key(
        "fk_purchase_predictions_analysis_run_id_analysis_runs",
        "purchase_predictions",
        "analysis_runs",
        ["analysis_run_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_purchase_predictions_customer_id_customers",
        "purchase_predictions",
        "customers",
        ["customer_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_purchase_predictions_model_version_id_model_registry",
        "purchase_predictions",
        "model_registry",
        ["model_version_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_purchase_predictions_analysis_run_id",
        "purchase_predictions",
        ["analysis_run_id"],
    )
    op.create_index(
        "ix_purchase_predictions_model_version_id",
        "purchase_predictions",
        ["model_version_id"],
    )

    config_id = uuid4()
    now = datetime.now(UTC)
    op.bulk_insert(
        sa.table(
            "configuration_versions",
            sa.column("id", sa.Uuid()),
            sa.column("created_at", sa.DateTime(timezone=True)),
            sa.column("updated_at", sa.DateTime(timezone=True)),
            sa.column("version", sa.String()),
            sa.column("status", sa.String()),
            sa.column("description", sa.String()),
            sa.column("effective_from", sa.DateTime(timezone=True)),
        ),
        [
            {
                "id": config_id,
                "created_at": now,
                "updated_at": now,
                "version": "CONFIG_DATASET_V1",
                "status": "ACTIVE",
                "description": "Dataset-aligned Phase 1 scoring and segmentation rules",
                "effective_from": now,
            }
        ],
    )
    scoring_table = sa.table(
        "scoring_rules",
        sa.column("id", sa.Uuid()),
        sa.column("configuration_version_id", sa.Uuid()),
        sa.column("component", sa.String()),
        sa.column("weight", sa.Numeric()),
        sa.column("enabled", sa.Boolean()),
    )
    op.bulk_insert(
        scoring_table,
        [
            {
                "id": uuid4(),
                "configuration_version_id": config_id,
                "component": "RECENCY",
                "weight": 0.35,
                "enabled": True,
            },
            {
                "id": uuid4(),
                "configuration_version_id": config_id,
                "component": "FREQUENCY",
                "weight": 0.30,
                "enabled": True,
            },
            {
                "id": uuid4(),
                "configuration_version_id": config_id,
                "component": "MONETARY",
                "weight": 0.20,
                "enabled": True,
            },
            {
                "id": uuid4(),
                "configuration_version_id": config_id,
                "component": "INTERACTION",
                "weight": 0.15,
                "enabled": True,
            },
        ],
    )
    threshold_table = sa.table(
        "segmentation_rules",
        sa.column("id", sa.Uuid()),
        sa.column("configuration_version_id", sa.Uuid()),
        sa.column("segment_code", sa.String()),
        sa.column("min_potential_score", sa.Numeric()),
        sa.column("max_potential_score", sa.Numeric()),
        sa.column("priority", sa.Integer()),
        sa.column("enabled", sa.Boolean()),
    )
    op.bulk_insert(
        threshold_table,
        [
            {
                "id": uuid4(),
                "configuration_version_id": config_id,
                "segment_code": "TIEM_NANG_CAO",
                "min_potential_score": 80,
                "max_potential_score": None,
                "priority": 1,
                "enabled": True,
            },
            {
                "id": uuid4(),
                "configuration_version_id": config_id,
                "segment_code": "TIEM_NANG",
                "min_potential_score": 60,
                "max_potential_score": 80,
                "priority": 2,
                "enabled": True,
            },
            {
                "id": uuid4(),
                "configuration_version_id": config_id,
                "segment_code": "THONG_THUONG",
                "min_potential_score": 0,
                "max_potential_score": 60,
                "priority": 3,
                "enabled": True,
            },
            {
                "id": uuid4(),
                "configuration_version_id": config_id,
                "segment_code": "CHUA_DU_DU_LIEU",
                "min_potential_score": None,
                "max_potential_score": None,
                "priority": 4,
                "enabled": True,
            },
        ],
    )
    valid_status_table = sa.table(
        "valid_order_status_configs",
        sa.column("id", sa.Uuid()),
        sa.column("configuration_version_id", sa.Uuid()),
        sa.column("order_status", sa.String()),
        sa.column("is_valid_for_analytics", sa.Boolean()),
    )
    op.bulk_insert(
        valid_status_table,
        [
            {
                "id": uuid4(),
                "configuration_version_id": config_id,
                "order_status": "PAID",
                "is_valid_for_analytics": True,
            },
            {
                "id": uuid4(),
                "configuration_version_id": config_id,
                "order_status": "COMPLETED",
                "is_valid_for_analytics": True,
            },
            {
                "id": uuid4(),
                "configuration_version_id": config_id,
                "order_status": "PARTIAL_REFUNDED",
                "is_valid_for_analytics": True,
            },
            {
                "id": uuid4(),
                "configuration_version_id": config_id,
                "order_status": "CANCELLED",
                "is_valid_for_analytics": False,
            },
            {
                "id": uuid4(),
                "configuration_version_id": config_id,
                "order_status": "FAILED",
                "is_valid_for_analytics": False,
            },
            {
                "id": uuid4(),
                "configuration_version_id": config_id,
                "order_status": "REFUNDED",
                "is_valid_for_analytics": False,
            },
        ],
    )


def downgrade() -> None:
    """Remove aligned models and restore the previous schema."""
    op.drop_index(
        "ix_purchase_predictions_model_version_id", table_name="purchase_predictions"
    )
    op.drop_index(
        "ix_purchase_predictions_analysis_run_id", table_name="purchase_predictions"
    )
    op.drop_constraint(
        "fk_purchase_predictions_model_version_id_model_registry",
        "purchase_predictions",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_purchase_predictions_customer_id_customers",
        "purchase_predictions",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_purchase_predictions_analysis_run_id_analysis_runs",
        "purchase_predictions",
        type_="foreignkey",
    )
    for name in ("analysis_run_id", "model_version_id", "feature_from", "feature_to"):
        op.drop_column("purchase_predictions", name)

    op.drop_index(
        "ix_segment_history_configuration_version_id", table_name="segment_history"
    )
    op.drop_index("ix_segment_history_analysis_run_id", table_name="segment_history")
    op.drop_constraint(
        "fk_segment_history_config_version_id",
        "segment_history",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_segment_history_customer_id_customers",
        "segment_history",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_segment_history_analysis_run_id_analysis_runs",
        "segment_history",
        type_="foreignkey",
    )
    for name in (
        "configuration_version_id",
        "segment_name",
        "segment_code",
        "analysis_run_id",
    ):
        op.drop_column("segment_history", name)

    op.drop_index("ix_model_registry_model_code", table_name="model_registry")
    for name in (
        "notes",
        "roc_auc",
        "f1_score",
        "recall",
        "precision",
        "prediction_horizon_days",
        "feature_window_days",
        "trained_at",
        "dataset_version",
        "model_type",
        "model_code",
    ):
        op.drop_column("model_registry", name)

    op.drop_index("ix_order_items_seller_id", table_name="order_items")
    op.drop_constraint(
        "fk_order_items_seller_id_sellers", "order_items", type_="foreignkey"
    )
    for name in (
        "shipping_limit_at",
        "line_total",
        "line_amount",
        "line_subtotal",
        "discount_value",
        "freight_value",
        "item_sequence",
        "seller_id",
    ):
        op.drop_column("order_items", name)

    for name in ("order_code", "source_order_id", "owner_id"):
        op.drop_index(f"ix_orders_{name}", table_name="orders")
    op.drop_constraint("fk_orders_owner_id_employees", "orders", type_="foreignkey")
    for name in (
        "is_valid_for_rfm",
        "currency",
        "province_city",
        "region",
        "sales_channel",
        "payment_method",
        "discount_total",
        "freight_total",
        "subtotal",
        "estimated_delivery_at",
        "delivered_customer_at",
        "delivered_carrier_at",
        "approved_at",
        "order_code",
        "source_order_id",
        "owner_id",
    ):
        op.drop_column("orders", name)

    for name in ("owner_id", "source_customer_id", "customer_code"):
        op.drop_index(f"ix_customers_{name}", table_name="customers")
    op.drop_constraint(
        "fk_customers_owner_id_employees", "customers", type_="foreignkey"
    )
    for name in (
        "owner_id",
        "registered_at",
        "province_city",
        "state_code",
        "city",
        "zip_code",
        "source_customer_id",
        "customer_code",
    ):
        op.drop_column("customers", name)

    op.drop_index("ix_users_employee_id", table_name="users")
    op.drop_constraint("fk_users_employee_id_employees", "users", type_="foreignkey")
    op.drop_column("users", "employee_id")

    op.drop_index("ix_audit_logs_entity", table_name="audit_logs")
    op.drop_index("ix_audit_logs_actor_id", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index("ix_import_errors_import_job_id", table_name="import_errors")
    op.drop_table("import_errors")
    op.drop_table("ml_model_evaluations")
    op.drop_table("customer_product_preferences")
    op.drop_table("customer_potential_score_history")
    op.drop_table("customer_behavior_history")
    op.drop_table("analysis_runs")
    op.drop_table("valid_order_status_configs")
    op.drop_table("segmentation_rules")
    op.drop_table("scoring_thresholds")
    op.drop_table("scoring_rules")
    op.drop_table("configuration_versions")
    op.drop_index("ix_customer_assignments_user_id", table_name="customer_assignments")
    op.drop_index(
        "ix_customer_assignments_customer_id", table_name="customer_assignments"
    )
    op.drop_table("customer_assignments")
    op.drop_table("user_roles")
    op.drop_index(
        "ix_customer_interactions_timestamp", table_name="customer_interactions"
    )
    op.drop_index(
        "ix_customer_interactions_campaign_id", table_name="customer_interactions"
    )
    op.drop_index(
        "ix_customer_interactions_product_id", table_name="customer_interactions"
    )
    op.drop_index(
        "ix_customer_interactions_customer_id", table_name="customer_interactions"
    )
    op.drop_table("customer_interactions")
    op.drop_index("ix_reviews_customer_id", table_name="reviews")
    op.drop_index("ix_reviews_order_id", table_name="reviews")
    op.drop_table("reviews")
    op.drop_index("ix_payments_order_id", table_name="payments")
    op.drop_table("payments")
    op.drop_table("campaigns")
    op.drop_table("geolocations")
    op.drop_table("sellers")
    op.drop_index("ix_employees_status", table_name="employees")
    op.drop_table("employees")
