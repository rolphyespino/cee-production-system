from flask import Flask

from app.blueprints import (
    admin,
    auth,
    catalog,
    clients,
    orders,
    payroll,
    production,
    quotes,
    reports,
    workers,
)
from app.cli import import_catalog, seed_users
from app.config import Config
from app.extensions import db, login_manager, migrate
from app.models import User


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth.bp)
    app.register_blueprint(workers.bp)
    app.register_blueprint(clients.bp)
    app.register_blueprint(catalog.bp)
    app.register_blueprint(quotes.bp)
    app.register_blueprint(orders.bp)
    app.register_blueprint(production.bp)
    app.register_blueprint(payroll.bp)
    app.register_blueprint(reports.bp)
    app.register_blueprint(admin.bp)

    app.cli.add_command(seed_users)
    app.cli.add_command(import_catalog)

    return app
