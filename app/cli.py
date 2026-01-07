import logging

import click
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import User
from app.models.enums import UserRole
from app.services.importer import import_catalog_from_excel


@click.command("seed-users")
def seed_users():
    users = [
        ("sales", "Sales User", UserRole.SALES),
        ("supervisor", "Supervisor User", UserRole.SUPERVISOR),
        ("admin", "Admin User", UserRole.ADMIN),
    ]
    for username, full_name, role in users:
        existing = User.query.filter_by(username=username).first()
        if existing:
            continue
        user = User(
            username=username,
            full_name=full_name,
            password_hash=generate_password_hash("password"),
            role=role,
        )
        db.session.add(user)
    db.session.commit()
    click.echo("Seeded users with default password 'password'.")


@click.command("import-catalog")
@click.argument("path")
def import_catalog(path):
    logging.basicConfig(level=logging.INFO)
    result = import_catalog_from_excel(path)
    db.session.commit()
    click.echo(f"Imported catalog: {result}")
