from sqlalchemy import CheckConstraint, Column, Date, DateTime, Enum, ForeignKey, Index, Integer, Numeric, Text

from app.extensions import db
from app.models.base import TimestampMixin
from app.models.enums import OrderLineStatus, OrderStatus, ServiceStatus


class Order(db.Model, TimestampMixin):
    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_status", "status"),
        Index("ix_orders_order_date", "order_date"),
        Index("ix_orders_due_date", "due_date"),
        Index("ix_orders_client_id", "client_id"),
    )

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    quote_id = Column(Integer, ForeignKey("quotes.id"))
    status = Column(Enum(OrderStatus), nullable=False)
    order_date = Column(Date, nullable=False)
    due_date = Column(Date)
    notes = Column(Text)
    subtotal_amount = Column(Numeric(12, 2), default=0, nullable=False)
    discount_amount = Column(Numeric(12, 2), default=0, nullable=False)
    total_amount = Column(Numeric(12, 2), default=0, nullable=False)

    deposit_required_percent = Column(Numeric(5, 2), default=0.50, nullable=False)
    deposit_amount = Column(Numeric(12, 2), default=0, nullable=False)
    deposit_exception = Column(db.Boolean, default=False, nullable=False)
    deposit_exception_reason = Column(Text)
    deposit_exception_by_user_id = Column(Integer, ForeignKey("users.id"))

    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    confirmed_by_user_id = Column(Integer, ForeignKey("users.id"))

    client = db.relationship("Client")
    quote = db.relationship("Quote")
    created_by = db.relationship("User", foreign_keys=[created_by_user_id])
    confirmed_by = db.relationship("User", foreign_keys=[confirmed_by_user_id])
    lines = db.relationship("OrderLine", back_populates="order", cascade="all, delete-orphan")


class OrderLine(db.Model, TimestampMixin):
    __tablename__ = "order_lines"
    __table_args__ = (
        CheckConstraint("qty > 0"),
        Index("ix_order_lines_order_status", "order_id", "status"),
        Index("ix_order_lines_assigned_worker", "assigned_worker_id"),
    )

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    catalog_item_id = Column(Integer, ForeignKey("catalog_items.id"), nullable=False)
    qty = Column(Integer, nullable=False)
    unit_rate = Column(Numeric(12, 2), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    line_total = Column(Numeric(12, 2), nullable=False)
    status = Column(Enum(OrderLineStatus), default=OrderLineStatus.PENDING, nullable=False)

    assigned_worker_id = Column(Integer, ForeignKey("workers.id"))
    assigned_by_user_id = Column(Integer, ForeignKey("users.id"))
    assigned_at = Column(DateTime)

    linked_garment_line_id = Column(Integer, ForeignKey("order_lines.id"))

    order = db.relationship("Order", back_populates="lines")
    catalog_item = db.relationship("CatalogItem")
    assigned_worker = db.relationship("Worker")
    assigned_by = db.relationship("User")
    linked_garment_line = db.relationship("OrderLine", remote_side=[id])


class OrderLineService(db.Model, TimestampMixin):
    __tablename__ = "order_line_services"
    __table_args__ = (CheckConstraint("qty > 0"),)

    id = Column(Integer, primary_key=True)
    order_line_id = Column(Integer, ForeignKey("order_lines.id"), nullable=False)
    service_catalog_item_id = Column(Integer, ForeignKey("catalog_items.id"), nullable=False)
    qty = Column(Integer, nullable=False)
    status = Column(Enum(ServiceStatus), default=ServiceStatus.PENDING, nullable=False)
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"))
    vendor_name = Column(db.String(120))
    notes = Column(Text)

    order_line = db.relationship("OrderLine")
    service_catalog_item = db.relationship("CatalogItem")
    assigned_to = db.relationship("User")
