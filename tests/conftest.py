from datetime import date

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.models import CatalogItem, Client, Order, OrderLine, User, Worker
from app.models.enums import ClientType, ItemType, OrderStatus, UserRole


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def session(app):
    return db.session


@pytest.fixture()
def users(session):
    sales = User(
        username="sales",
        full_name="Sales",
        password_hash=generate_password_hash("x"),
        role=UserRole.SALES,
    )
    supervisor = User(
        username="supervisor",
        full_name="Supervisor",
        password_hash=generate_password_hash("x"),
        role=UserRole.SUPERVISOR,
    )
    admin = User(
        username="admin",
        full_name="Admin",
        password_hash=generate_password_hash("x"),
        role=UserRole.ADMIN,
    )
    session.add_all([sales, supervisor, admin])
    session.commit()
    return sales, supervisor, admin


@pytest.fixture()
def catalog_items(session):
    garment = CatalogItem(item_type=ItemType.GARMENT, code="GAR-1", name="Garment")
    service = CatalogItem(item_type=ItemType.SERVICE, code="SER-1", name="Service")
    session.add_all([garment, service])
    session.commit()
    return garment, service


@pytest.fixture()
def worker(session):
    worker = Worker(code="OP-001", full_name="Worker")
    session.add(worker)
    session.commit()
    return worker


@pytest.fixture()
def client(session):
    client = Client(client_type=ClientType.COMPANY, name="Acme")
    session.add(client)
    session.commit()
    return client


@pytest.fixture()
def order(session, users, client):
    sales, _, _ = users
    order = Order(
        client_id=client.id,
        status=OrderStatus.DRAFT,
        order_date=date(2026, 1, 1),
        created_by_user_id=sales.id,
        deposit_required_percent=0.5,
        deposit_amount=0,
    )
    session.add(order)
    session.commit()
    return order
