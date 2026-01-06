"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2026-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


user_role = sa.Enum("SALES", "SUPERVISOR", "ADMIN", name="user_role")
client_type = sa.Enum("COMPANY", "INDIVIDUAL", name="client_type")
item_type = sa.Enum("GARMENT", "SERVICE", name="item_type")
rate_type = sa.Enum("CONFECCION", name="rate_type")
quote_status = sa.Enum("DRAFT", "SENT", "APPROVED", "REJECTED", name="quote_status")
order_status = sa.Enum("DRAFT", "CONFIRMED", "IN_PRODUCTION", "CLOSED", "CANCELLED", name="order_status")
order_line_status = sa.Enum("PENDING", "ASSIGNED", "IN_PRODUCTION", "DONE", name="order_line_status")
service_status = sa.Enum("PENDING", "IN_PROGRESS", "DONE", "OUTSOURCED", name="service_status")
production_status = sa.Enum("INCOMPLETE", "VALIDATED", name="production_status")
payroll_status = sa.Enum("PRELIMINARY", "APPROVED", "PAID", name="payroll_status")
change_request_status = sa.Enum("PENDING", "APPROVED", "REJECTED", name="change_request_status")


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(length=80), nullable=False, unique=True),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "workers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("code", sa.String(length=20), nullable=False, unique=True),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("id_number", sa.String(length=50)),
        sa.Column("phone", sa.String(length=50)),
        sa.Column("hire_date", sa.Date),
        sa.Column("termination_date", sa.Date),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "clients",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("client_type", client_type, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("rnc_or_id", sa.String(length=50)),
        sa.Column("email", sa.String(length=120)),
        sa.Column("phone", sa.String(length=50)),
        sa.Column("address", sa.Text),
        sa.Column("notes", sa.Text),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "catalog_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("item_type", item_type, nullable=False),
        sa.Column("code", sa.String(length=120), nullable=False, unique=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("notes", sa.Text),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("linea", sa.String(length=80)),
        sa.Column("familia", sa.String(length=80)),
        sa.Column("subfamilia", sa.String(length=80)),
        sa.Column("version", sa.String(length=80)),
        sa.Column("aplica_personalizacion", sa.Boolean),
        sa.Column("service_type", sa.String(length=80)),
        sa.Column("service_subtype", sa.String(length=80)),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "piece_rates",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("catalog_item_id", sa.Integer, sa.ForeignKey("catalog_items.id"), nullable=False),
        sa.Column("rate_type", rate_type, nullable=False),
        sa.Column("rate_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("effective_from", sa.Date, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.UniqueConstraint("catalog_item_id", "rate_type", "effective_from"),
    )

    op.create_table(
        "quotes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("client_id", sa.Integer, sa.ForeignKey("clients.id"), nullable=False),
        sa.Column("status", quote_status, nullable=False),
        sa.Column("notes", sa.Text),
        sa.Column("subtotal_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("discount_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("created_by_user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "quote_lines",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("quote_id", sa.Integer, sa.ForeignKey("quotes.id"), nullable=False),
        sa.Column("catalog_item_id", sa.Integer, sa.ForeignKey("catalog_items.id"), nullable=False),
        sa.Column("qty", sa.Integer, nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("line_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("linked_garment_line_id", sa.Integer, sa.ForeignKey("quote_lines.id")),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.CheckConstraint("qty > 0"),
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("client_id", sa.Integer, sa.ForeignKey("clients.id"), nullable=False),
        sa.Column("quote_id", sa.Integer, sa.ForeignKey("quotes.id")),
        sa.Column("status", order_status, nullable=False),
        sa.Column("order_date", sa.Date, nullable=False),
        sa.Column("due_date", sa.Date),
        sa.Column("notes", sa.Text),
        sa.Column("subtotal_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("discount_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("deposit_required_percent", sa.Numeric(5, 2), nullable=False, server_default="0.50"),
        sa.Column("deposit_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("deposit_exception", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("deposit_exception_reason", sa.Text),
        sa.Column("deposit_exception_by_user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("created_by_user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("confirmed_by_user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_orders_status", "orders", ["status"])
    op.create_index("ix_orders_order_date", "orders", ["order_date"])
    op.create_index("ix_orders_due_date", "orders", ["due_date"])
    op.create_index("ix_orders_client_id", "orders", ["client_id"])

    op.create_table(
        "order_lines",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("order_id", sa.Integer, sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("catalog_item_id", sa.Integer, sa.ForeignKey("catalog_items.id"), nullable=False),
        sa.Column("qty", sa.Integer, nullable=False),
        sa.Column("unit_rate", sa.Numeric(12, 2), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("line_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", order_line_status, nullable=False, server_default="PENDING"),
        sa.Column("assigned_worker_id", sa.Integer, sa.ForeignKey("workers.id")),
        sa.Column("assigned_by_user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("assigned_at", sa.DateTime),
        sa.Column("linked_garment_line_id", sa.Integer, sa.ForeignKey("order_lines.id")),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.CheckConstraint("qty > 0"),
    )
    op.create_index("ix_order_lines_order_status", "order_lines", ["order_id", "status"])
    op.create_index("ix_order_lines_assigned_worker", "order_lines", ["assigned_worker_id"])

    op.create_table(
        "order_line_services",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("order_line_id", sa.Integer, sa.ForeignKey("order_lines.id"), nullable=False),
        sa.Column("service_catalog_item_id", sa.Integer, sa.ForeignKey("catalog_items.id"), nullable=False),
        sa.Column("qty", sa.Integer, nullable=False),
        sa.Column("status", service_status, nullable=False, server_default="PENDING"),
        sa.Column("assigned_to_user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("vendor_name", sa.String(length=120)),
        sa.Column("notes", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.CheckConstraint("qty > 0"),
    )

    op.create_table(
        "production_entries",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("order_line_id", sa.Integer, sa.ForeignKey("order_lines.id"), nullable=False),
        sa.Column("worker_id", sa.Integer, sa.ForeignKey("workers.id"), nullable=False),
        sa.Column("entry_date", sa.Date, nullable=False),
        sa.Column("qty_done", sa.Integer, nullable=False),
        sa.Column("status", production_status, nullable=False, server_default="INCOMPLETE"),
        sa.Column("notes", sa.Text),
        sa.Column("created_by_user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("validated_by_user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("validated_at", sa.DateTime),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.CheckConstraint("qty_done > 0"),
    )

    op.create_table(
        "payroll_runs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("period_start", sa.Date, nullable=False),
        sa.Column("period_end", sa.Date, nullable=False),
        sa.Column("status", payroll_status, nullable=False, server_default="PRELIMINARY"),
        sa.Column("created_by_user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("approved_by_user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.UniqueConstraint("period_start", "period_end"),
    )

    op.create_table(
        "payroll_lines",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("payroll_run_id", sa.Integer, sa.ForeignKey("payroll_runs.id"), nullable=False),
        sa.Column("worker_id", sa.Integer, sa.ForeignKey("workers.id"), nullable=False),
        sa.Column("pieces_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "change_requests",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("order_id", sa.Integer, sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("requested_by_user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("payload_json", sa.JSON, nullable=False),
        sa.Column("status", change_request_status, nullable=False, server_default="PENDING"),
        sa.Column("decided_by_user_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("decided_at", sa.DateTime),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("entity_type", sa.String(length=40), nullable=False),
        sa.Column("entity_id", sa.Integer, nullable=False),
        sa.Column("action", sa.String(length=60), nullable=False),
        sa.Column("actor_user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("details_json", sa.JSON),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_audit_entity", "audit_logs", ["entity_type", "entity_id"])
    op.create_index("ix_audit_actor", "audit_logs", ["actor_user_id"])
    op.create_index("ix_audit_created", "audit_logs", ["created_at"])


def downgrade():
    op.drop_index("ix_audit_created", table_name="audit_logs")
    op.drop_index("ix_audit_actor", table_name="audit_logs")
    op.drop_index("ix_audit_entity", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_table("change_requests")
    op.drop_table("payroll_lines")
    op.drop_table("payroll_runs")
    op.drop_table("production_entries")
    op.drop_table("order_line_services")
    op.drop_index("ix_order_lines_assigned_worker", table_name="order_lines")
    op.drop_index("ix_order_lines_order_status", table_name="order_lines")
    op.drop_table("order_lines")
    op.drop_index("ix_orders_client_id", table_name="orders")
    op.drop_index("ix_orders_due_date", table_name="orders")
    op.drop_index("ix_orders_order_date", table_name="orders")
    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_table("orders")
    op.drop_table("quote_lines")
    op.drop_table("quotes")
    op.drop_table("piece_rates")
    op.drop_table("catalog_items")
    op.drop_table("clients")
    op.drop_table("workers")
    op.drop_table("users")

    change_request_status.drop(op.get_bind(), checkfirst=True)
    payroll_status.drop(op.get_bind(), checkfirst=True)
    production_status.drop(op.get_bind(), checkfirst=True)
    service_status.drop(op.get_bind(), checkfirst=True)
    order_line_status.drop(op.get_bind(), checkfirst=True)
    order_status.drop(op.get_bind(), checkfirst=True)
    quote_status.drop(op.get_bind(), checkfirst=True)
    rate_type.drop(op.get_bind(), checkfirst=True)
    item_type.drop(op.get_bind(), checkfirst=True)
    client_type.drop(op.get_bind(), checkfirst=True)
    user_role.drop(op.get_bind(), checkfirst=True)
