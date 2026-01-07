from sqlalchemy import CheckConstraint, Column, Date, DateTime, Enum, ForeignKey, Integer, Text

from app.extensions import db
from app.models.base import TimestampMixin
from app.models.enums import ProductionStatus


class ProductionEntry(db.Model, TimestampMixin):
    __tablename__ = "production_entries"
    __table_args__ = (CheckConstraint("qty_done > 0"),)

    id = Column(Integer, primary_key=True)
    order_line_id = Column(Integer, ForeignKey("order_lines.id"), nullable=False)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    entry_date = Column(Date, nullable=False)
    qty_done = Column(Integer, nullable=False)
    status = Column(Enum(ProductionStatus), default=ProductionStatus.INCOMPLETE, nullable=False)
    notes = Column(Text)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    validated_by_user_id = Column(Integer, ForeignKey("users.id"))
    validated_at = Column(DateTime)

    order_line = db.relationship("OrderLine")
    worker = db.relationship("Worker")
    created_by = db.relationship("User", foreign_keys=[created_by_user_id])
    validated_by = db.relationship("User", foreign_keys=[validated_by_user_id])
