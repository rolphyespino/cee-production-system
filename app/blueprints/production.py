from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import OrderLine, ProductionEntry
from app.models.enums import UserRole
from app.services import production as production_service
from app.services.authz import require_role


bp = Blueprint("production", __name__, url_prefix="/production")


@bp.route("/")
@login_required
@require_role(UserRole.SUPERVISOR)
def index():
    entries = ProductionEntry.query.order_by(ProductionEntry.id.desc()).all()
    return render_template("production/index.html", entries=entries)


@bp.route("/new", methods=["GET", "POST"])
@login_required
@require_role(UserRole.SUPERVISOR)
def create():
    if request.method == "POST":
        order_line = OrderLine.query.get(request.form.get("order_line_id"))
        try:
            entry_date = date.fromisoformat(request.form.get("entry_date"))
            production_service.create_production_entry(
                order_line,
                worker_id=request.form.get("worker_id"),
                entry_date=entry_date,
                qty_done=int(request.form.get("qty_done")),
                actor_user=current_user,
            )
            db.session.commit()
            flash("Production entry created", "success")
        except production_service.ProductionError as exc:
            db.session.rollback()
            flash(str(exc), "error")
        return redirect(url_for("production.index"))
    return render_template("production/new.html")


@bp.route("/<int:entry_id>/validate", methods=["POST"])
@login_required
@require_role(UserRole.SUPERVISOR)
def validate(entry_id):
    entry = ProductionEntry.query.get_or_404(entry_id)
    try:
        production_service.validate_production_entry(entry, current_user)
        db.session.commit()
        flash("Entry validated", "success")
    except production_service.ProductionError as exc:
        db.session.rollback()
        flash(str(exc), "error")
    return redirect(url_for("production.index"))
