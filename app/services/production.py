from datetime import datetime
from decimal import Decimal

from sqlalchemy import func

from app.extensions import db
from app.models import OrderLine, OrderLineService, ProductionEntry
from app.models.enums import ItemType, OrderLineStatus, ProductionStatus, ServiceStatus
from app.services.audit import log_action


class ProductionError(ValueError):
    pass


def create_production_entry(order_line: OrderLine, worker_id, entry_date, qty_done, actor_user):
    if order_line.catalog_item.item_type != ItemType.GARMENT:
        raise ProductionError("Production entries are only allowed for GARMENT lines")
    entry = ProductionEntry(
        order_line_id=order_line.id,
        worker_id=worker_id,
        entry_date=entry_date,
        qty_done=qty_done,
        status=ProductionStatus.INCOMPLETE,
        created_by_user_id=actor_user.id,
    )
    db.session.add(entry)
    log_action(
        entity_type="ProductionEntry",
        entity_id=order_line.id,
        action="CREATED",
        actor_user_id=actor_user.id,
        details={"qty_done": qty_done},
    )
    return entry


def validate_production_entry(entry: ProductionEntry, supervisor_user):
    if entry.status != ProductionStatus.INCOMPLETE:
        raise ProductionError("Entry already validated")

    validated_qty = (
        db.session.query(func.coalesce(func.sum(ProductionEntry.qty_done), 0))
        .filter(
            ProductionEntry.order_line_id == entry.order_line_id,
            ProductionEntry.status == ProductionStatus.VALIDATED,
        )
        .scalar()
    )
    new_total = Decimal(validated_qty) + Decimal(entry.qty_done)
    if new_total > Decimal(entry.order_line.qty):
        raise ProductionError("Validated quantity exceeds order line quantity")

    entry.status = ProductionStatus.VALIDATED
    entry.validated_by_user_id = supervisor_user.id
    entry.validated_at = datetime.utcnow()

    if new_total == Decimal(entry.order_line.qty):
        if _services_completed(entry.order_line):
            entry.order_line.status = OrderLineStatus.DONE
    log_action(
        entity_type="ProductionEntry",
        entity_id=entry.id,
        action="VALIDATED",
        actor_user_id=supervisor_user.id,
        details={"new_total": str(new_total)},
    )
    return entry


def _services_completed(order_line: OrderLine) -> bool:
    services = OrderLineService.query.filter_by(order_line_id=order_line.id).all()
    if not services:
        return True
    return all(service.status in {ServiceStatus.DONE, ServiceStatus.OUTSOURCED} for service in services)
