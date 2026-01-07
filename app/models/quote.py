from sqlalchemy import CheckConstraint, Column, Enum, ForeignKey, Integer, Numeric, Text

from app.extensions import db
from app.models.base import TimestampMixin
from app.models.enums import QuoteStatus


class Quote(db.Model, TimestampMixin):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    status = Column(Enum(QuoteStatus), nullable=False)
    notes = Column(Text)
    subtotal_amount = Column(Numeric(12, 2), default=0, nullable=False)
    discount_amount = Column(Numeric(12, 2), default=0, nullable=False)
    total_amount = Column(Numeric(12, 2), default=0, nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    client = db.relationship("Client")
    created_by = db.relationship("User")
    lines = db.relationship("QuoteLine", back_populates="quote", cascade="all, delete-orphan")


class QuoteLine(db.Model, TimestampMixin):
    __tablename__ = "quote_lines"
    __table_args__ = (CheckConstraint("qty > 0"),)

    id = Column(Integer, primary_key=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False)
    catalog_item_id = Column(Integer, ForeignKey("catalog_items.id"), nullable=False)
    qty = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    line_total = Column(Numeric(12, 2), nullable=False)
    linked_garment_line_id = Column(Integer, ForeignKey("quote_lines.id"))

    quote = db.relationship("Quote", back_populates="lines")
    catalog_item = db.relationship("CatalogItem")
    linked_garment_line = db.relationship("QuoteLine", remote_side=[id])
