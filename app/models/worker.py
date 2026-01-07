from sqlalchemy import Boolean, Column, Date, Integer, String, Text

from app.extensions import db
from app.models.base import TimestampMixin


class Worker(db.Model, TimestampMixin):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    full_name = Column(String(120), nullable=False)
    id_number = Column(String(50))
    phone = Column(String(50))
    hire_date = Column(Date)
    termination_date = Column(Date)
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text)
