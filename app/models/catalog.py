from sqlalchemy import Boolean, Column, Date, Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint

from app.extensions import db
from app.models.base import TimestampMixin
from app.models.enums import ItemType, RateType


class CatalogItem(db.Model, TimestampMixin):
    __tablename__ = "catalog_items"

    id = Column(Integer, primary_key=True)
    item_type = Column(Enum(ItemType), nullable=False)
    code = Column(String(120), unique=True, nullable=False)
    name = Column(String(150), nullable=False)
    notes = Column(Text)
    is_active = Column(Boolean, default=True, nullable=False)

    linea = Column(String(80))
    familia = Column(String(80))
    subfamilia = Column(String(80))
    version = Column(String(80))
    aplica_personalizacion = Column(Boolean)

    service_type = Column(String(80))
    service_subtype = Column(String(80))


class PieceRate(db.Model, TimestampMixin):
    __tablename__ = "piece_rates"
    __table_args__ = (
        UniqueConstraint("catalog_item_id", "rate_type", "effective_from"),
    )

    id = Column(Integer, primary_key=True)
    catalog_item_id = Column(Integer, ForeignKey("catalog_items.id"), nullable=False)
    rate_type = Column(Enum(RateType), nullable=False)
    rate_amount = Column(Numeric(12, 2), nullable=False)
    effective_from = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    catalog_item = db.relationship("CatalogItem")
