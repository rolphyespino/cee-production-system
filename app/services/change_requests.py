from datetime import datetime

from app.extensions import db
from app.models import ChangeRequest, Order
from app.models.enums import ChangeRequestStatus, OrderStatus
from app.services.audit import log_action


class ChangeRequestError(ValueError):
    pass


def create_change_request(order: Order, requested_by, reason: str, payload: dict):
    if order.status != OrderStatus.CONFIRMED:
        raise ChangeRequestError("Change requests only allowed for CONFIRMED orders")
    if not reason:
        raise ChangeRequestError("Reason is required")
    change_request = ChangeRequest(
        order_id=order.id,
        requested_by_user_id=requested_by.id,
        reason=reason,
        payload_json=payload,
    )
    db.session.add(change_request)
    log_action(
        entity_type="ChangeRequest",
        entity_id=order.id,
        action="REQUESTED",
        actor_user_id=requested_by.id,
        details={"reason": reason},
    )
    return change_request


def decide_change_request(change_request: ChangeRequest, decided_by, approved: bool):
    if change_request.status != ChangeRequestStatus.PENDING:
        raise ChangeRequestError("Change request already decided")

    change_request.status = ChangeRequestStatus.APPROVED if approved else ChangeRequestStatus.REJECTED
    change_request.decided_by_user_id = decided_by.id
    change_request.decided_at = datetime.utcnow()

    action = "APPROVED" if approved else "REJECTED"
    log_action(
        entity_type="ChangeRequest",
        entity_id=change_request.id,
        action=action,
        actor_user_id=decided_by.id,
        details={"payload": change_request.payload_json},
    )

    if approved:
        _apply_change_payload(change_request.order, change_request.payload_json)
    return change_request


def _apply_change_payload(order: Order, payload: dict):
    before = {"status": order.status.value, "total_amount": str(order.total_amount)}
    updates = payload.get("updates", {})
    allowed_fields = {"notes", "due_date", "total_amount", "discount_amount", "subtotal_amount"}
    for field, value in updates.items():
        if field in allowed_fields:
            setattr(order, field, value)
    db.session.flush()
    log_action(
        entity_type="Order",
        entity_id=order.id,
        action="CHANGE_APPLIED",
        actor_user_id=order.created_by_user_id,
        details={"before": before, "after": updates},
    )
