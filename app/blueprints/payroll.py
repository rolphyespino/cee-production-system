from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import PayrollRun
from app.models.enums import UserRole
from app.services import payroll as payroll_service
from app.services.authz import require_role


bp = Blueprint("payroll", __name__, url_prefix="/payroll")


@bp.route("/")
@login_required
@require_role(UserRole.SUPERVISOR)
def index():
    runs = PayrollRun.query.order_by(PayrollRun.id.desc()).all()
    return render_template("payroll/index.html", runs=runs)


@bp.route("/generate", methods=["POST"])
@login_required
@require_role(UserRole.SUPERVISOR)
def generate():
    period_start = date.fromisoformat(request.form.get("period_start"))
    period_end = date.fromisoformat(request.form.get("period_end"))
    payroll_service.generate_payroll_run(period_start, period_end, current_user)
    db.session.commit()
    flash("Payroll run generated", "success")
    return redirect(url_for("payroll.index"))
