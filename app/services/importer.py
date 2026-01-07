import logging
import re
import math
from datetime import date
from decimal import Decimal, InvalidOperation

import pandas as pd

from app.extensions import db
from app.models import CatalogItem, PieceRate
from app.models.enums import ItemType, RateType


LOGGER = logging.getLogger(__name__)


def normalize_code(value: str) -> str:
    if value is None:
        return ""
    value = str(value).strip().lower()
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"[^a-z0-9\-]", "", value)
    return value.upper()


def _is_nan(value) -> bool:
    # pandas/Excel often gives float('nan') for empty numeric cells
    try:
        return isinstance(value, float) and math.isnan(value)
    except Exception:
        return False


def _to_decimal_or_zero(value) -> Decimal:
    """
    Convert Excel/pandas numeric cell to Decimal.
    If empty/None/NaN/invalid => Decimal('0').
    """
    if value is None or value == "" or _is_nan(value):
        return Decimal("0")

    try:
        # value can be int/float/str; Decimal(str(...)) is safest
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0")


def import_catalog_from_excel(path: str):
    prendas = pd.read_excel(path, sheet_name="Matriz_Prendas")
    servicios = pd.read_excel(path, sheet_name="Matriz_Servicios")
    _ = pd.read_excel(path, sheet_name="Matriz_Ofertas")

    # Avoid premature flush while we're still building objects
    with db.session.no_autoflush:
        for _, row in prendas.iterrows():
            linea = row.get("Línea") or row.get("Linea")
            familia = row.get("Familia")
            subfamilia = row.get("Subfamilia")
            version = row.get("Versión") or row.get("Version")
            if not all([linea, familia, subfamilia, version]):
                LOGGER.warning("Skipping garment row with missing fields: %s", row)
                continue

            code = (
                f"GAR-{normalize_code(linea)}-"
                f"{normalize_code(familia)}-"
                f"{normalize_code(subfamilia)}-"
                f"{normalize_code(version)}"
            )
            name = f"{familia} {subfamilia} – {version}"
            aplica = str(row.get("Aplica Personalizacion? Y/N", "")).strip().upper() == "Y"

            catalog_item = CatalogItem.query.filter_by(code=code).first()
            if catalog_item:
                LOGGER.info("Duplicate garment code skipped: %s", code)
                continue

            catalog_item = CatalogItem(
                item_type=ItemType.GARMENT,
                code=code,
                name=name,
                linea=linea,
                familia=familia,
                subfamilia=subfamilia,
                version=version,
                aplica_personalizacion=aplica,
            )
            db.session.add(catalog_item)
            db.session.flush()  # get catalog_item.id

            # FIX: handle NaN/empty/invalid values safely
            rate_value = row.get("Mano de Obra - Confección (RD$)")
            rate_amount = _to_decimal_or_zero(rate_value)

            piece_rate = PieceRate(
                catalog_item_id=catalog_item.id,
                rate_type=RateType.CONFECCION,
                rate_amount=rate_amount,  # never NaN / never None
                effective_from=date(2026, 1, 1),
                is_active=True,
            )
            db.session.add(piece_rate)

        for _, row in servicios.iterrows():
            tipo = row.get("Tipo de Servicio")
            subtipo = row.get("Subtipo/Tamaño")
            if not all([tipo, subtipo]):
                LOGGER.warning("Skipping service row with missing fields: %s", row)
                continue

            code = f"SER-{normalize_code(tipo)}-{normalize_code(subtipo)}"
            name = f"{tipo} - {subtipo}"

            catalog_item = CatalogItem.query.filter_by(code=code).first()
            if catalog_item:
                LOGGER.info("Duplicate service code skipped: %s", code)
                continue

            catalog_item = CatalogItem(
                item_type=ItemType.SERVICE,
                code=code,
                name=name,
                service_type=tipo,
                service_subtype=subtipo,
            )
            db.session.add(catalog_item)

    LOGGER.info("Matriz_Ofertas loaded for reference only; no tables created.")
    return {
        "garments": len(prendas.index),
        "services": len(servicios.index),
    }
