from sqlalchemy import Column, Enum, ForeignKey, Integer, JSON, Text

from app.extensions import db
from app.models.base import TimestampMixin
from app.models.enums import ChangeRequestStatus


class ChangeRequest(db.Model, TimestampMixin):
    __tablename__ = "change_requests"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    requested_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(Text, nullable=False)
    payload_json = Column(JSON, nullable=False)
    status = Column(Enum(ChangeRequestStatus), default=ChangeRequestStatus.PENDING, nullable=False)
    decided_by_user_id = Column(Integer, ForeignKey("users.id"))
    decided_at = Column(db.DateTime)

    order = db.relationship("Order")
    requested_by = db.relationship("User", foreign_keys=[requested_by_user_id])
    decided_by = db.relationship("User", foreign_keys=[decided_by_user_id])
