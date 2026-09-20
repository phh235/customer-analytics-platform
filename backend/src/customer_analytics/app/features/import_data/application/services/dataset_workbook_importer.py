"""Persistence orchestration for the canonical dataset workbook."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import date, datetime
from decimal import Decimal
from statistics import mean
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from customer_analytics.app.features.analytics.infrastructure.models.aligned import (
    AnalysisRunModel,
    ConfigurationVersionModel,
    CustomerBehaviorHistoryModel,
    CustomerPotentialScoreHistoryModel,
)
from customer_analytics.app.features.analytics.infrastructure.models.analytics_history import (
    SegmentHistoryModel,
)
from customer_analytics.app.features.customer.infrastructure.models.customer import (
    CustomerModel,
)
from customer_analytics.app.features.import_data.application.services.dataset_contract import (
    DatasetWorkbook,
    bool_value,
    canonical_currency,
    canonical_order_status,
    clean_text,
    datetime_value,
    decimal_value,
    int_value,
    is_missing,
)
from customer_analytics.app.features.import_data.domain.entities.import_job import (
    ImportError,
    ImportJob,
)
from customer_analytics.app.features.order.infrastructure.models.order import (
    OrderItemModel,
    OrderModel,
)
from customer_analytics.app.features.product.infrastructure.models.product import (
    ProductModel,
)
from customer_analytics.app.features.reference_data.infrastructure.models import (
    CampaignModel,
    CustomerInteractionModel,
    EmployeeModel,
    GeolocationModel,
    PaymentModel,
    ReviewModel,
    SellerModel,
)

IMPORT_ID_NAMESPACE = uuid.UUID("3f5a6d1f-9b48-4f54-8b2b-5ac8b0ad7a11")


class DatasetWorkbookImporter:
    """Import workbook sheets in contract order with row-level idempotency."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.job: ImportJob | None = None
        self._customers: dict[str, CustomerModel] = {}
        self._products: dict[str, ProductModel] = {}
        self._employees: dict[str, EmployeeModel] = {}
        self._sellers: dict[str, SellerModel] = {}
        self._campaigns: dict[str, CampaignModel] = {}
        self._orders: dict[str, OrderModel] = {}

    async def run(self, workbook: DatasetWorkbook, job: ImportJob) -> ImportJob:
        """Persist every importable sheet and return updated job state."""
        self.job = job.start_processing()
        handlers: tuple[tuple[str, Callable[[dict[str, Any]], Any]], ...] = (
            ("Employees", self._employee),
            ("Campaigns", self._campaign),
            ("Sellers", self._seller),
            ("Geolocation", self._geolocation),
            ("Products", self._product),
            ("Customers", self._customer),
            ("Orders", self._order),
            ("OderItems", self._order_item),
            ("Payments", self._payment),
            ("Reviews", self._review),
            ("Interactions", self._interaction),
            ("ModelRuns", self._model_run),
            ("CustomerAnalytics", self._customer_analytics),
        )
        for sheet_name, handler in handlers:
            for row_number, row in enumerate(workbook.sheets[sheet_name].rows, start=2):
                await self._run_row(sheet_name, row_number, row, handler)

        await self._refresh_customer_statistics()
        return self.job.complete() if self.job else job

    async def _run_row(
        self,
        sheet: str,
        row_number: int,
        row: dict[str, Any],
        handler: Callable[[dict[str, Any]], Any],
    ) -> None:
        try:
            async with self.session.begin_nested():
                await handler(row)
                await self.session.flush()
        except Exception as exc:
            self._error(
                sheet,
                row_number,
                "row",
                "ROW_IMPORT_FAILED",
                str(exc),
                row,
            )
        else:
            self.job = self.job.increment_processed(True) if self.job else self.job

    def _error(
        self,
        sheet: str,
        row_number: int,
        field: str,
        error_code: str,
        message: str,
        raw_value: Any,
    ) -> None:
        if self.job is None:
            return
        self.job = self.job.add_error(
            ImportError(
                sheet=sheet,
                row_number=row_number,
                field=field,
                error_code=error_code,
                message=message,
                raw_value=self._json_safe(raw_value),
            )
        )
        self.job = self.job.increment_processed(False)

    @classmethod
    def _json_safe(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return {str(key): cls._json_safe(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [cls._json_safe(item) for item in value]
        if isinstance(value, (datetime, date, Decimal, uuid.UUID)):
            return str(value)
        return value

    @staticmethod
    def _stable_id(value: Any, entity_type: str) -> uuid.UUID:
        if value is None or value == "":
            return uuid.uuid4()
        try:
            return uuid.UUID(str(value))
        except ValueError:
            return uuid.uuid5(IMPORT_ID_NAMESPACE, f"{entity_type}:{value}")

    async def _one(self, model: Any, **filters: Any) -> Any | None:
        result = await self.session.execute(select(model).filter_by(**filters).limit(1))
        return result.scalar_one_or_none()

    async def _employee(self, row: dict[str, Any]) -> None:
        code = clean_text(row["employee_id"])
        name = clean_text(row["employee_name"])
        if not code or not name:
            raise ValueError("employee_id và employee_name là bắt buộc")
        model = await self._one(EmployeeModel, employee_code=code)
        if model is None:
            model = EmployeeModel(
                id=self._stable_id(code, "employee"), employee_code=code
            )
            self.session.add(model)
        model.name = name
        model.department = clean_text(row["department"])
        model.email = clean_text(row["email"])
        model.phone = clean_text(row["phone"])
        model.region_scope = clean_text(row["region_scope"])
        model.status = (clean_text(row["status"]) or "ACTIVE").upper()
        model.start_date = datetime_value(row["start_date"], date_only=True)
        self._employees[code] = model

    async def _campaign(self, row: dict[str, Any]) -> None:
        code = clean_text(row["campaign_id"])
        name = clean_text(row["campaign_name"])
        if not code or not name:
            raise ValueError("campaign_id và campaign_name là bắt buộc")
        model = await self._one(CampaignModel, campaign_code=code)
        if model is None:
            model = CampaignModel(
                id=self._stable_id(code, "campaign"), campaign_code=code
            )
            self.session.add(model)
        model.name = name
        model.campaign_type = clean_text(row["campaign_type"])
        model.start_date = datetime_value(row["start_date"], date_only=True)
        model.end_date = datetime_value(row["end_date"], date_only=True)
        model.channel = clean_text(row["channel"])
        model.target_segment = clean_text(row["target_segment"])
        model.status = (clean_text(row["status"]) or "ACTIVE").upper()
        model.budget_vnd = decimal_value(row["budget_vnd"])
        self._campaigns[code] = model

    async def _seller(self, row: dict[str, Any]) -> None:
        code = clean_text(row["seller_id"])
        if not code:
            raise ValueError("seller_id là bắt buộc")
        model = await self._one(SellerModel, seller_code=code)
        if model is None:
            model = SellerModel(id=self._stable_id(code, "seller"), seller_code=code)
            self.session.add(model)
        model.seller_name = clean_text(row["SellerName"])
        model.zip_code = clean_text(row["seller_zip_code_prefix"])
        model.city = clean_text(row["seller_city"])
        model.state_code = clean_text(row["seller_state"])
        model.region = clean_text(row["Region"])
        self._sellers[code] = model

    async def _geolocation(self, row: dict[str, Any]) -> None:
        code = clean_text(row["geolocation_zip_code_prefix"])
        if not code:
            raise ValueError("geolocation_zip_code_prefix là bắt buộc")
        model = await self._one(GeolocationModel, zip_code=code)
        if model is None:
            model = GeolocationModel(
                id=self._stable_id(code, "geolocation"), zip_code=code
            )
            self.session.add(model)
        model.latitude = decimal_value(row["geolocation_lat"])
        model.longitude = decimal_value(row["geolocation_lng"])
        model.city = clean_text(row["geolocation_city"])
        model.state_code = clean_text(row["geolocation_state"])
        model.region = clean_text(row["Region"])

    async def _product(self, row: dict[str, Any]) -> None:
        source_id = clean_text(row["product_id"])
        if not source_id:
            raise ValueError("product_id là bắt buộc")
        model = await self._one(ProductModel, source_product_id=source_id)
        if model is None:
            model = ProductModel(
                id=self._stable_id(source_id, "product"),
                source_product_id=source_id,
                product_code=source_id,
            )
            self.session.add(model)
        model.name = clean_text(row["Description"]) or source_id
        model.category = (
            clean_text(row["ProductCategory"])
            or clean_text(row["product_category_name"])
            or "UNSPECIFIED"
        )
        model.source_category_code = clean_text(row["product_category_name"])
        model.description = clean_text(row["Description"])
        model.price = decimal_value(row["ListPrice"])
        model.list_price = decimal_value(row["ListPrice"])
        model.currency = canonical_currency(row["Currency"])
        model.weight_g = decimal_value(row["product_weight_g"])
        model.length_cm = decimal_value(row["product_length_cm"])
        model.height_cm = decimal_value(row["product_height_cm"])
        model.width_cm = decimal_value(row["product_width_cm"])
        model.photo_count = int_value(row["product_photos_qty"])
        model.status = (clean_text(row["ProductStatus"]) or "ACTIVE").upper()
        self._products[source_id] = model

    async def _customer(self, row: dict[str, Any]) -> None:
        source_id = clean_text(row["customer_id"])
        code = clean_text(row["customer_unique_id"])
        name = clean_text(row["CustomerName"])
        if not source_id or not code or not name:
            raise ValueError(
                "customer_id, customer_unique_id và CustomerName là bắt buộc"
            )
        model = await self._one(CustomerModel, source_customer_id=source_id)
        if model is None:
            model = CustomerModel(
                id=self._stable_id(source_id, "customer"),
                source_customer_id=source_id,
            )
            self.session.add(model)
        owner_code = clean_text(row["owner_id"])
        owner = self._employees.get(owner_code or "")
        if owner is None and owner_code:
            owner = await self._one(EmployeeModel, employee_code=owner_code)
        model.customer_code = code
        model.name = name
        model.zip_code = clean_text(row["customer_zip_code_prefix"])
        model.city = clean_text(row["customer_city"])
        model.state_code = clean_text(row["customer_state"])
        model.province_city = clean_text(row["ProvinceCity"])
        model.email = clean_text(row["Email"])
        model.phone = clean_text(row["Phone"])
        model.registered_at = datetime_value(row["RegisteredDate"])
        model.customer_since = model.registered_at
        model.owner_id = owner.id if owner else None
        model.status = (clean_text(row["CustomerStatus"]) or "ACTIVE").upper()
        self._customers[source_id] = model
        self._customers[code] = model

    async def _order(self, row: dict[str, Any]) -> None:
        source_id = clean_text(row["order_id"])
        if not source_id:
            raise ValueError("order_id là bắt buộc")
        customer_ref = clean_text(row["customer_id"])
        customer = self._customers.get(customer_ref or "")
        if customer is None and customer_ref:
            customer = await self._one(CustomerModel, source_customer_id=customer_ref)
        if customer is None:
            raise ValueError(f"Không tìm thấy customer_id={customer_ref!r}")
        model = await self._one(OrderModel, source_order_id=source_id)
        if model is None:
            model = OrderModel(
                id=self._stable_id(source_id, "order"),
                source_order_id=source_id,
                order_number=source_id,
            )
            self.session.add(model)
        owner_code = clean_text(row["owner_id"])
        owner = self._employees.get(owner_code or "")
        if owner is None and owner_code:
            owner = await self._one(EmployeeModel, employee_code=owner_code)
        status = canonical_order_status(row["order_status"])
        total = decimal_value(row["OrderTotal"])
        model.customer_id = customer.id
        model.order_code = source_id
        model.order_date = datetime_value(row["order_purchase_timestamp"])
        if model.order_date is None:
            raise ValueError("order_purchase_timestamp là bắt buộc")
        model.approved_at = datetime_value(row["order_approved_at"])
        model.delivered_carrier_at = datetime_value(row["order_delivered_carrier_date"])
        model.delivered_customer_at = datetime_value(
            row["order_delivered_customer_date"]
        )
        model.estimated_delivery_at = datetime_value(
            row["order_estimated_delivery_date"]
        )
        model.owner_id = owner.id if owner else None
        model.subtotal = decimal_value(row["OrderSubtotal"])
        model.freight_total = decimal_value(row["FreightTotal"])
        model.discount_total = decimal_value(row["DiscountTotal"])
        model.payment_method = clean_text(row["PaymentMethod"])
        model.sales_channel = clean_text(row["SalesChannel"])
        model.region = clean_text(row["Region"])
        model.province_city = clean_text(row["ProvinceCity"])
        model.currency = canonical_currency(row["Currency"])
        model.is_valid_for_rfm = bool_value(row["IsValidForRFM"], status == "DELIVERED")
        model.total_amount = total
        model.refund_amount = Decimal("0")
        model.net_amount = total
        model.status = status
        model.channel = model.sales_channel
        self._orders[source_id] = model

    async def _order_item(self, row: dict[str, Any]) -> None:
        order_ref = clean_text(row["order_id"])
        product_ref = clean_text(row["product_id"])
        if not order_ref or not product_ref:
            raise ValueError("order_id và product_id là bắt buộc")
        order = self._orders.get(order_ref) or await self._one(
            OrderModel, source_order_id=order_ref
        )
        product = self._products.get(product_ref) or await self._one(
            ProductModel, source_product_id=product_ref
        )
        if order is None or product is None:
            raise ValueError("Không tìm thấy order hoặc product tham chiếu")
        sequence = int_value(row["order_item_id"], 1)
        model = await self._one(
            OrderItemModel, order_id=order.id, item_sequence=sequence
        )
        if model is None:
            model = OrderItemModel(
                id=self._stable_id(f"{order_ref}:{sequence}", "order_item"),
                order_id=order.id,
                item_sequence=sequence,
            )
            self.session.add(model)
        quantity = int_value(row["Quantity"], 1)
        unit_price = decimal_value(row["price"])
        line_amount = decimal_value(row["LineAmount"], unit_price * quantity)
        model.product_id = product.id
        seller_ref = clean_text(row["seller_id"])
        seller = self._sellers.get(seller_ref or "")
        model.seller_id = seller.id if seller else None
        model.quantity = quantity
        model.unit_price = unit_price
        model.freight_value = decimal_value(row["freight_value"])
        model.discount_value = decimal_value(row["discount_value"])
        model.line_subtotal = decimal_value(row["line_subtotal"], line_amount)
        model.line_amount = line_amount
        model.line_total = decimal_value(row["line_total"], line_amount)
        model.shipping_limit_at = datetime_value(row["shipping_limit_date"])
        model.subtotal = model.line_subtotal or line_amount

    async def _payment(self, row: dict[str, Any]) -> None:
        order_ref = clean_text(row["order_id"])
        order = self._orders.get(order_ref or "")
        if order is None and order_ref:
            order = await self._one(OrderModel, source_order_id=order_ref)
        if order is None:
            raise ValueError(f"Không tìm thấy order_id={order_ref!r}")
        sequence = int_value(row["payment_sequential"], 1)
        model = await self._one(
            PaymentModel, order_id=order.id, payment_sequence=sequence
        )
        if model is None:
            model = PaymentModel(
                id=self._stable_id(f"{order_ref}:{sequence}", "payment"),
                order_id=order.id,
                payment_sequence=sequence,
                payment_value=Decimal("0"),
            )
            self.session.add(model)
        model.payment_type = clean_text(row["payment_type"])
        model.payment_method = clean_text(row["PaymentMethodVN"])
        model.payment_installments = int_value(row["payment_installments"])
        model.payment_value = decimal_value(row["payment_value"])
        model.currency = canonical_currency(row["Currency"])

    async def _review(self, row: dict[str, Any]) -> None:
        code = clean_text(row["review_id"])
        order_ref = clean_text(row["order_id"])
        order = self._orders.get(order_ref or "")
        customer_ref = clean_text(row["CustomerID"])
        customer = self._customers.get(customer_ref or "")
        if order is None or customer is None:
            raise ValueError("Review phải tham chiếu order và customer hợp lệ")
        score = int_value(row["review_score"])
        if not 1 <= score <= 5:
            raise ValueError("review_score phải nằm trong khoảng 1..5")
        model = await self._one(ReviewModel, review_code=code) if code else None
        if model is None:
            model = ReviewModel(
                id=self._stable_id(code or f"{order_ref}:{score}", "review"),
                review_code=code,
                order_id=order.id,
                customer_id=customer.id,
                score=score,
            )
            self.session.add(model)
        model.order_id = order.id
        model.customer_id = customer.id
        model.score = score
        model.title = clean_text(row["review_comment_title"])
        model.message = clean_text(row["review_comment_message"])
        model.review_created_at = datetime_value(row["review_creation_date"])
        model.answered_at = datetime_value(row["review_answer_timestamp"])
        model.channel = clean_text(row["Channel"])

    async def _interaction(self, row: dict[str, Any]) -> None:
        code = clean_text(row["interaction_id"])
        customer_ref = clean_text(row["customer_unique_id"])
        product_ref = clean_text(row["product_id"])
        customer = self._customers.get(customer_ref or "")
        product = self._products.get(product_ref or "")
        if customer is None or product is None:
            raise ValueError("Interaction phải tham chiếu customer và product hợp lệ")
        campaign_ref = clean_text(row["campaign_id"])
        campaign = (
            None if campaign_ref == "1583" else self._campaigns.get(campaign_ref or "")
        )
        if campaign is None and campaign_ref and campaign_ref != "1583":
            campaign = await self._one(CampaignModel, campaign_code=campaign_ref)
        model = await self._one(CustomerInteractionModel, interaction_code=code)
        if model is None:
            model = CustomerInteractionModel(
                id=self._stable_id(
                    code or f"{customer_ref}:{product_ref}", "interaction"
                ),
                interaction_code=code,
                customer_id=customer.id,
                product_id=product.id,
                interaction_type=clean_text(row["interaction_type"]) or "UNKNOWN",
                interaction_timestamp=datetime_value(row["interaction_timestamp"]),
                interaction_value=Decimal("0"),
            )
            self.session.add(model)
        timestamp = datetime_value(row["interaction_timestamp"])
        if timestamp is None:
            raise ValueError("interaction_timestamp là bắt buộc")
        model.customer_id = customer.id
        model.product_id = product.id
        model.campaign_id = campaign.id if campaign else None
        model.interaction_type = clean_text(row["interaction_type"]) or "UNKNOWN"
        model.interaction_timestamp = timestamp
        model.channel = clean_text(row["channel"])
        model.session_id = clean_text(row["session_id"])
        model.interaction_value = decimal_value(row["interaction_value"])
        model.interaction_result = clean_text(row["interaction_result"])
        model.is_mock_data = True

    async def _model_run(self, row: dict[str, Any]) -> None:
        code = clean_text(row["run_id"])
        analysis_date = datetime_value(row["analysis_date"], date_only=True)
        if not code or analysis_date is None:
            raise ValueError("run_id và analysis_date là bắt buộc")
        config = await self._one(
            ConfigurationVersionModel, version="DATASET_CONTRACT_V1"
        )
        if config is None:
            config = ConfigurationVersionModel(
                id=self._stable_id("DATASET_CONTRACT_V1", "configuration"),
                version="DATASET_CONTRACT_V1",
                status="ACTIVE",
                description="Canonical dataset workbook import",
            )
            self.session.add(config)
            await self.session.flush()
        model = await self._one(AnalysisRunModel, run_code=code)
        if model is None:
            model = AnalysisRunModel(
                id=self._stable_id(code, "analysis_run"),
                run_code=code,
                analysis_type=clean_text(row["model_type"]) or "UNKNOWN",
                status=(clean_text(row["status"]) or "PENDING").upper(),
                analysis_date=analysis_date,
            )
            self.session.add(model)
        model.analysis_type = clean_text(row["model_type"]) or "UNKNOWN"
        model.status = (clean_text(row["status"]) or "PENDING").upper()
        model.analysis_date = analysis_date
        model.total_records = int_value(row["record_count"])
        model.success_records = (
            model.total_records if model.status == "COMPLETED" else 0
        )
        model.failed_records = 0
        model.configuration_version_id = config.id
        model.error_message = clean_text(row["notes"])
        model.started_at = datetime_value(row["run_timestamp"])
        model.completed_at = model.started_at if model.status == "COMPLETED" else None
        await self.session.flush()
        await self._clear_run_history(model.id)

    async def _customer_analytics(self, row: dict[str, Any]) -> None:
        customer_ref = clean_text(row["CustomerID"])
        customer = self._customers.get(customer_ref or "")
        if customer is None:
            customer = await self._one(CustomerModel, customer_code=customer_ref)
        if customer is None:
            raise ValueError(f"Không tìm thấy CustomerID={customer_ref!r}")
        run = await self._latest_run_for_date(
            datetime_value(row["AnalysisDate"], date_only=True)
        )
        if run is None:
            raise ValueError("Không tìm thấy ModelRun tương ứng với AnalysisDate")
        valid_orders = await self._customer_orders(customer.id)
        dates = sorted(order.order_date.date() for order in valid_orders)
        analysis_date = run.analysis_date
        recency = (analysis_date - dates[-1]).days if dates else None
        frequency = len(valid_orders)
        monetary = sum((order.net_amount for order in valid_orders), Decimal("0"))
        aov = monetary / frequency if frequency else Decimal("0")
        cycles = [
            (second - first).days
            for first, second in zip(dates, dates[1:], strict=False)
        ]
        average_cycle = Decimal(str(mean(cycles))) if cycles else None
        review_scores = await self._review_scores(customer.id)
        avg_review = (
            sum(review_scores, Decimal("0")) / len(review_scores)
            if review_scores
            else None
        )
        interaction_score = decimal_value(row["InteractionScore"])
        potential_score = self._safe_decimal(row["PotentialScore"])
        level = clean_text(row["ModelStatus"]) or "INSUFFICIENT_DATA"
        if not valid_orders:
            potential_score = None
            level = "INSUFFICIENT_DATA"

        self.session.add(
            CustomerBehaviorHistoryModel(
                id=self._stable_id(f"{run.id}:{customer.id}", "behavior"),
                analysis_run_id=run.id,
                customer_id=customer.id,
                recency_days=recency,
                frequency=frequency,
                monetary=monetary,
                aov=aov,
                avg_purchase_cycle_days=average_cycle,
                avg_review_score=avg_review,
            )
        )
        self.session.add(
            CustomerPotentialScoreHistoryModel(
                id=self._stable_id(f"{run.id}:{customer.id}", "potential"),
                analysis_run_id=run.id,
                customer_id=customer.id,
                r_score=self._safe_decimal(row["RScore"]) if valid_orders else None,
                f_score=self._safe_decimal(row["FScore"]) if valid_orders else None,
                m_score=self._safe_decimal(row["MScore"]) if valid_orders else None,
                interaction_score=interaction_score,
                potential_score=potential_score,
                potential_level=level,
                configuration_version_id=run.configuration_version_id,
            )
        )
        self.session.add(
            SegmentHistoryModel(
                id=self._stable_id(f"{run.id}:{customer.id}", "segment"),
                analysis_run_id=run.id,
                customer_id=customer.id,
                segment_type="CUSTOMER_ANALYTICS",
                segment_code=clean_text(row["Segment"]),
                segment_name=clean_text(row["Segment"]),
                reason="Imported from canonical CustomerAnalytics snapshot",
                configuration_version_id=run.configuration_version_id,
                calculated_at=datetime_value(row["AnalysisDate"]),
            )
        )

    async def _clear_run_history(self, run_id: uuid.UUID) -> None:
        for model in (
            CustomerBehaviorHistoryModel,
            CustomerPotentialScoreHistoryModel,
            SegmentHistoryModel,
        ):
            await self.session.execute(
                delete(model).where(model.analysis_run_id == run_id)
            )

    async def _latest_run_for_date(
        self, analysis_date: date | None
    ) -> AnalysisRunModel | None:
        if analysis_date is None:
            return None
        result = await self.session.execute(
            select(AnalysisRunModel)
            .where(AnalysisRunModel.analysis_date == analysis_date)
            .order_by(AnalysisRunModel.run_code)
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _customer_orders(self, customer_id: uuid.UUID) -> list[OrderModel]:
        result = await self.session.execute(
            select(OrderModel)
            .where(
                OrderModel.customer_id == customer_id,
                OrderModel.is_valid_for_rfm.is_(True),
            )
            .order_by(OrderModel.order_date)
        )
        return list(result.scalars().all())

    async def _review_scores(self, customer_id: uuid.UUID) -> list[Decimal]:
        result = await self.session.execute(
            select(ReviewModel.score).where(ReviewModel.customer_id == customer_id)
        )
        return [Decimal(str(score)) for score in result.scalars().all()]

    async def _refresh_customer_statistics(self) -> None:
        result = await self.session.execute(select(CustomerModel))
        customers = list(result.scalars().all())
        for customer in customers:
            orders = await self._customer_orders(customer.id)
            customer.total_orders = len(orders)
            customer.total_spent = sum(
                (order.net_amount for order in orders), Decimal("0")
            )
            customer.avg_order_value = (
                customer.total_spent / customer.total_orders
                if customer.total_orders
                else Decimal("0")
            )
            customer.last_purchase_date = orders[-1].order_date if orders else None

    @staticmethod
    def _safe_decimal(value: Any) -> Decimal | None:
        if is_missing(value):
            return None
        try:
            return decimal_value(value)
        except ValueError:
            return None


async def import_dataset_workbook(
    session: AsyncSession,
    workbook: DatasetWorkbook,
    job: ImportJob,
) -> ImportJob:
    """Convenience entry point used by the import use case."""
    return await DatasetWorkbookImporter(session).run(workbook, job)
