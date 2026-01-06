from flask import Blueprint, render_template
from flask_login import login_required

from app.models.enums import UserRole
from app.services.authz import require_role


bp = Blueprint("reports", __name__, url_prefix="/")


@bp.route("/")
@login_required
@require_role(UserRole.SALES)
def index():
    return render_template("reports/index.html")


@bp.route("/reports/orders-confirmed")
@login_required
@require_role(UserRole.SALES)
def orders_confirmed():
    return render_template("reports/placeholder.html", title="Orders Confirmed")


@bp.route("/reports/production-by-worker")
@login_required
@require_role(UserRole.SUPERVISOR)
def production_by_worker():
    return render_template("reports/placeholder.html", title="Production by Worker")


@bp.route("/reports/delivery-status")
@login_required
@require_role(UserRole.SALES)
def delivery_status():
    return render_template("reports/placeholder.html", title="Delivery Status")


@bp.route("/reports/payroll-projection")
@login_required
@require_role(UserRole.SUPERVISOR)
def payroll_projection():
    return render_template("reports/placeholder.html", title="Payroll Projection")


@bp.route("/reports/executive-summary")
@login_required
@require_role(UserRole.SUPERVISOR)
def executive_summary():
    return render_template("reports/placeholder.html", title="Executive Summary")
