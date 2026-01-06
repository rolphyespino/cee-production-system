from datetime import date
from decimal import Decimal

import pytest

from app.extensions import db
from app.models import OrderLine, OrderLineService, ProductionEntry
from app.models.enums import ChangeRequestStatus, ItemType, OrderLineStatus, OrderStatus, ProductionStatus
from app.services import change_requests as change_request_service
from app.services import orders as order_service
from app.services import payroll as payroll_service
from app.services import production as production_service


def test_confirm_order_requires_deposit(order, users, catalog_items, session):
    sales, supervisor, _ = users
    garment, service = catalog_items
    line = OrderLine(
        order_id=order.id,
        catalog_item_id=garment.id,
        qty=10,
        unit_rate=Decimal("5"),
        unit_price=Decimal("100"),
        line_total=Decimal("1000"),
    )
    session.add(line)
    session.commit()

    order.total_amount = Decimal("1000")
    order.deposit_amount = Decimal("100")
    with pytest.raises(order_service.OrderError):
        order_service.confirm_order(order, sales)

    order_service.set_deposit_exception(order, supervisor, "Approved")
    order_service.confirm_order(order, sales)
    session.commit()

    assert order.status == OrderStatus.CONFIRMED


def test_deposit_exception_requires_supervisor(order, users):
    sales, _, _ = users
    with pytest.raises(order_service.OrderError):
        order_service.set_deposit_exception(order, sales, "No deposit")


def test_change_request_admin_approval(order, users):
    sales, _, admin = users
    order.status = OrderStatus.CONFIRMED
    db.session.commit()

    change_request = change_request_service.create_change_request(
        order,
        requested_by=sales,
        reason="Update notes",
        payload={"updates": {"notes": "New note"}},
    )
    db.session.commit()

    assert change_request.status == ChangeRequestStatus.PENDING

    change_request_service.decide_change_request(change_request, admin, approved=True)
    db.session.commit()

    assert change_request.status == ChangeRequestStatus.APPROVED
    assert order.notes == "New note"


def test_production_validation_limits(order, users, catalog_items, worker, session):
    _, supervisor, _ = users
    garment, _ = catalog_items
    line = OrderLine(
        order_id=order.id,
        catalog_item_id=garment.id,
        qty=5,
        unit_rate=Decimal("3"),
        unit_price=Decimal("50"),
        line_total=Decimal("250"),
    )
    session.add(line)
    session.commit()

    entry = production_service.create_production_entry(
        line, worker.id, date(2026, 1, 1), 3, supervisor
    )
    session.commit()
    production_service.validate_production_entry(entry, supervisor)
    session.commit()

    entry2 = production_service.create_production_entry(
        line, worker.id, date(2026, 1, 2), 3, supervisor
    )
    session.commit()
    with pytest.raises(production_service.ProductionError):
        production_service.validate_production_entry(entry2, supervisor)


def test_production_entries_only_for_garments(order, users, catalog_items, worker):
    _, supervisor, _ = users
    _, service = catalog_items
    line = OrderLine(
        order_id=order.id,
        catalog_item_id=service.id,
        qty=5,
        unit_rate=Decimal("0"),
        unit_price=Decimal("10"),
        line_total=Decimal("50"),
    )
    db.session.add(line)
    db.session.commit()

    with pytest.raises(production_service.ProductionError):
        production_service.create_production_entry(
            line, worker.id, date(2026, 1, 1), 1, supervisor
        )


def test_payroll_calculation(order, users, catalog_items, worker, session):
    _, supervisor, _ = users
    garment, _ = catalog_items
    line = OrderLine(
        order_id=order.id,
        catalog_item_id=garment.id,
        qty=5,
        unit_rate=Decimal("4"),
        unit_price=Decimal("50"),
        line_total=Decimal("250"),
    )
    session.add(line)
    session.commit()

    entry = ProductionEntry(
        order_line_id=line.id,
        worker_id=worker.id,
        entry_date=date(2026, 1, 1),
        qty_done=5,
        status=ProductionStatus.VALIDATED,
        created_by_user_id=supervisor.id,
    )
    session.add(entry)
    session.commit()

    run = payroll_service.generate_payroll_run(date(2026, 1, 1), date(2026, 1, 15), supervisor)
    session.commit()

    assert run.lines[0].pieces_count == 5
    assert Decimal(run.lines[0].amount) == Decimal("20")


def test_generate_order_line_services(order, users, catalog_items, session):
    sales, supervisor, _ = users
    garment, service = catalog_items
    garment_line = OrderLine(
        order_id=order.id,
        catalog_item_id=garment.id,
        qty=2,
        unit_rate=Decimal("3"),
        unit_price=Decimal("30"),
        line_total=Decimal("60"),
    )
    session.add(garment_line)
    session.flush()
    service_line = OrderLine(
        order_id=order.id,
        catalog_item_id=service.id,
        qty=2,
        unit_rate=Decimal("0"),
        unit_price=Decimal("5"),
        line_total=Decimal("10"),
        linked_garment_line_id=garment_line.id,
    )
    session.add(service_line)
    session.commit()

    order.status = OrderStatus.DRAFT
    order.deposit_exception = True
    order.deposit_exception_reason = "Approved"
    order.deposit_exception_by_user_id = supervisor.id
    order.total_amount = Decimal("70")
    session.commit()

    order_service.confirm_order(order, sales)
    session.commit()

    services = OrderLineService.query.filter_by(order_line_id=garment_line.id).all()
    assert services
