import logging
import re
from datetime import date
from decimal import Decimal

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


def import_catalog_from_excel(path: str):
    prendas = pd.read_excel(path, sheet_name="Matriz_Prendas")
    servicios = pd.read_excel(path, sheet_name="Matriz_Servicios")
    _ = pd.read_excel(path, sheet_name="Matriz_Ofertas")

    for _, row in prendas.iterrows():
        linea = row.get("Línea") or row.get("Linea")
        familia = row.get("Familia")
        subfamilia = row.get("Subfamilia")
        version = row.get("Versión") or row.get("Version")
        if not all([linea, familia, subfamilia, version]):
            LOGGER.warning("Skipping garment row with missing fields: %s", row)
            continue
        code = f"GAR-{normalize_code(linea)}-{normalize_code(familia)}-{normalize_code(subfamilia)}-{normalize_code(version)}"
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
        db.session.flush()

        rate_value = row.get("Mano de Obra - Confección (RD$)")
        rate_amount = Decimal(rate_value) if rate_value not in (None, "") else Decimal("0")
        piece_rate = PieceRate(
            catalog_item_id=catalog_item.id,
            rate_type=RateType.CONFECCION,
            rate_amount=rate_amount,
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
