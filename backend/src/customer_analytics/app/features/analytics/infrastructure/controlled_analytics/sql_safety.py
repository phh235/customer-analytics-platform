"""AST-based safety policy for model-generated analytics SQL."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NoReturn

from sqlglot import exp, parse
from sqlglot.errors import ParseError

from customer_analytics.app.config import Settings
from customer_analytics.app.features.analytics.domain.semantic_layer import (
    ADMIN_RAW_TABLES,
    ALLOWED_RESULT_ALIASES,
    ANALYTICS_VIEWS,
)
from customer_analytics.app.shared.errors import ErrorCode
from customer_analytics.app.shared.exceptions import AppException


@dataclass(frozen=True)
class ValidatedQuery:
    """Canonical SQL accepted by the safety policy."""

    sql: str
    tables: frozenset[str]


class SQLSafetyGateway:
    """Validate untrusted SQL before it can reach the read-only database."""

    def __init__(self, config: Settings, *, admin_mode: bool = False) -> None:
        self._config = config
        self._admin_mode = admin_mode
        view_columns = frozenset(
            column for columns in ANALYTICS_VIEWS.values() for column in columns
        )
        raw_columns = (
            frozenset(
                column for columns in ADMIN_RAW_TABLES.values() for column in columns
            )
            if admin_mode
            else frozenset()
        )
        self._allowed_columns = view_columns | raw_columns | ALLOWED_RESULT_ALIASES
        self._allowed_tables = frozenset(ANALYTICS_VIEWS)

    def validate(self, sql: str) -> ValidatedQuery:
        """Parse and validate one PostgreSQL SELECT statement."""
        if len(sql) > self._config.AI_ANALYTICS_MAX_SQL_LENGTH:
            self._reject("SQL exceeds the configured length limit.")

        try:
            statements = parse(sql, read="postgres")
        except ParseError as exc:
            self._reject("SQL could not be parsed.", cause=exc)

        if len(statements) != 1:
            self._reject("Only one SQL statement is allowed.")

        expression = statements[0]
        if not isinstance(expression, exp.Select):
            self._reject("Only SELECT statements are allowed.")
        if not self._admin_mode:
            for star in expression.find_all(exp.Star):
                if not isinstance(star.parent, exp.Count):
                    self._reject("SELECT * is not allowed.")
        for function in expression.find_all(exp.Func):
            if isinstance(function, exp.Condition):
                continue
            if function.sql_name() not in {
                "AVG",
                "CAST",
                "COALESCE",
                "COUNT",
                "DATE_TRUNC",
                "EXTRACT",
                "MAX",
                "MIN",
                "NULLIF",
                "ROUND",
                "SUM",
                "TIMESTAMP_TRUNC",
            }:
                self._reject(f"Function '{function.sql_name()}' is not allowed.")
        tables: set[str] = set()
        for table in expression.find_all(exp.Table):
            if table.db == "analytics" and table.name in self._allowed_tables:
                qualified_name = f"analytics.{table.name}"
            elif (
                self._admin_mode
                and table.name in ADMIN_RAW_TABLES
                and table.db in {None, "", "public"}
            ):
                qualified_name = f"public.{table.name}"
            else:
                self._reject("Only whitelisted analytics tables are allowed.")
            tables.add(qualified_name)

        if not tables:
            self._reject("The query must read an approved analytics table.")

        for column in expression.find_all(exp.Column):
            if column.name not in self._allowed_columns:
                self._reject(f"Column '{column.name}' is not allowed.")

        if (
            len(list(expression.find_all(exp.Join)))
            > self._config.AI_ANALYTICS_MAX_JOINS
        ):
            self._reject("Query join complexity exceeds the configured limit.")

        limit = expression.args.get("limit")
        if limit is None:
            expression = expression.limit(self._config.AI_ANALYTICS_MAX_RESULT_ROWS)
        else:
            literal = limit.expression
            if not isinstance(literal, exp.Literal) or not literal.is_int:
                self._reject("LIMIT must be a positive integer.")
            limit_value = int(literal.this)
            if (
                limit_value < 1
                or limit_value > self._config.AI_ANALYTICS_MAX_RESULT_ROWS
            ):
                self._reject("LIMIT exceeds the configured row limit.")

        return ValidatedQuery(
            sql=expression.sql(dialect="postgres"),
            tables=frozenset(tables),
        )

    @staticmethod
    def _reject(message: str, *, cause: Exception | None = None) -> NoReturn:
        error = AppException(ErrorCode.ANALYTICS_QUERY_REJECTED, message=message)
        if cause is not None:
            raise error from cause
        raise error
