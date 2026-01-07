from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, Numeric, UniqueConstraint

from app.extensions import db
from app.models.base import TimestampMixin
from app.models.enums import PayrollStatus


class PayrollRun(db.Model, TimestampMixin):
    __tablename__ = "payroll_runs"
    __table_args__ = (UniqueConstraint("period_start", "period_end"),)

    id = Column(Integer, primary_key=True)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    status = Column(Enum(PayrollStatus), default=PayrollStatus.PRELIMINARY, nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by_user_id = Column(Integer, ForeignKey("users.id"))

    created_by = db.relationship("User", foreign_keys=[created_by_user_id])
    approved_by = db.relationship("User", foreign_keys=[approved_by_user_id])
    lines = db.relationship("PayrollLine", back_populates="payroll_run", cascade="all, delete-orphan")


class PayrollLine(db.Model, TimestampMixin):
    __tablename__ = "payroll_lines"

    id = Column(Integer, primary_key=True)
    payroll_run_id = Column(Integer, ForeignKey("payroll_runs.id"), nullable=False)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    pieces_count = Column(Integer, default=0, nullable=False)
    amount = Column(Numeric(12, 2), default=0, nullable=False)

    payroll_run = db.relationship("PayrollRun", back_populates="lines")
    worker = db.relationship("Worker")
