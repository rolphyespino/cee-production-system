from sqlalchemy import Boolean, Column, Enum, Integer, String, Text

from app.extensions import db
from app.models.base import TimestampMixin
from app.models.enums import ClientType


class Client(db.Model, TimestampMixin):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True)
    client_type = Column(Enum(ClientType), nullable=False)
    name = Column(String(150), nullable=False)
    rnc_or_id = Column(String(50))
    email = Column(String(120))
    phone = Column(String(50))
    address = Column(Text)
    notes = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)
