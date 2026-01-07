from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.extensions import db
from app.models import Worker
from app.services.authz import require_role
from app.models.enums import UserRole


bp = Blueprint("workers", __name__, url_prefix="/workers")


@bp.route("/")
@login_required
@require_role(UserRole.SALES)
def index():
    workers = Worker.query.order_by(Worker.full_name).all()
    return render_template("workers/index.html", workers=workers)


@bp.route("/new", methods=["GET", "POST"])
@login_required
@require_role(UserRole.SUPERVISOR)
def create():
    if request.method == "POST":
        worker = Worker(
            code=request.form.get("code"),
            full_name=request.form.get("full_name"),
        )
        db.session.add(worker)
        db.session.commit()
        flash("Worker created", "success")
        return redirect(url_for("workers.index"))
    return render_template("workers/new.html")
