from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.extensions import db
from app.models import Client
from app.models.enums import ClientType, UserRole
from app.services.authz import require_role


bp = Blueprint("clients", __name__, url_prefix="/clients")


@bp.route("/")
@login_required
@require_role(UserRole.SALES)
def index():
    clients = Client.query.order_by(Client.name).all()
    return render_template("clients/index.html", clients=clients)


@bp.route("/new", methods=["GET", "POST"])
@login_required
@require_role(UserRole.SALES)
def create():
    if request.method == "POST":
        client = Client(
            client_type=ClientType(request.form.get("client_type")),
            name=request.form.get("name"),
        )
        db.session.add(client)
        db.session.commit()
        flash("Client created", "success")
        return redirect(url_for("clients.index"))
    return render_template("clients/new.html")
