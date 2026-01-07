from datetime import datetime
from decimal import Decimal

from app.extensions import db
from app.models import Order, OrderLine, OrderLineService
from app.models.enums import ItemType, OrderLineStatus, OrderStatus, ServiceStatus, UserRole
from app.services.audit import log_action


class OrderError(ValueError):
    pass


def calculate_order_total(order: Order) -> Decimal:
    return sum((line.line_total for line in order.lines), Decimal("0"))


def confirm_order(order: Order, actor_user):
    if order.status != OrderStatus.DRAFT:
        raise OrderError("Order is not in DRAFT status")

    estimated_total = order.total_amount or calculate_order_total(order)
    required_deposit = Decimal(order.deposit_required_percent) * Decimal(estimated_total)

    if order.deposit_exception:
        if not order.deposit_exception_reason or not order.deposit_exception_by_user_id:
            raise OrderError("Deposit exception requires reason and supervisor")
    else:
        if Decimal(order.deposit_amount) < required_deposit:
            raise OrderError("Deposit amount does not meet required minimum")

    order.status = OrderStatus.CONFIRMED
    order.confirmed_by_user_id = actor_user.id
    log_action(
        entity_type="Order",
        entity_id=order.id,
        action="CONFIRMED",
        actor_user_id=actor_user.id,
        details={"required_deposit": str(required_deposit)},
    )
    generate_order_line_services(order, actor_user)
    return order


def set_deposit_exception(order: Order, supervisor_user, reason: str):
    if supervisor_user.role != UserRole.SUPERVISOR and supervisor_user.role != UserRole.ADMIN:
        raise OrderError("Only supervisor can set deposit exception")
    if not reason:
        raise OrderError("Deposit exception reason is required")

    order.deposit_exception = True
    order.deposit_exception_reason = reason
    order.deposit_exception_by_user_id = supervisor_user.id
    log_action(
        entity_type="Order",
        entity_id=order.id,
        action="DEPOSIT_EXCEPTION",
        actor_user_id=supervisor_user.id,
        details={"reason": reason},
    )
    return order


def generate_order_line_services(order: Order, actor_user):
    created = []
    for line in order.lines:
        if line.catalog_item.item_type != ItemType.SERVICE:
            continue
        if not line.linked_garment_line_id:
            continue
        service = OrderLineService(
            order_line_id=line.linked_garment_line_id,
            service_catalog_item_id=line.catalog_item_id,
            qty=line.qty,
            status=ServiceStatus.PENDING,
        )
        db.session.add(service)
        created.append(service)
        log_action(
            entity_type="OrderLineService",
            entity_id=line.linked_garment_line_id,
            action="SERVICE_TRACK_CREATED",
            actor_user_id=actor_user.id,
            details={"service_line_id": line.id},
        )
    return created


def assign_worker(order_line: OrderLine, worker_id: int, actor_user):
    if order_line.catalog_item.item_type != ItemType.GARMENT:
        raise OrderError("Only GARMENT lines can be assigned to workers")
    order_line.assigned_worker_id = worker_id
    order_line.assigned_by_user_id = actor_user.id
    order_line.assigned_at = datetime.utcnow()
    order_line.status = OrderLineStatus.ASSIGNED
    log_action(
        entity_type="OrderLine",
        entity_id=order_line.id,
        action="ASSIGNED",
        actor_user_id=actor_user.id,
        details={"worker_id": worker_id},
    )
    return order_line
