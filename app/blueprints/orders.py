from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Order, OrderLine
from app.models.enums import OrderStatus, UserRole
from app.services import change_requests as change_request_service
from app.services import orders as order_service
from app.services.authz import require_role


bp = Blueprint("orders", __name__, url_prefix="/orders")


@bp.route("/")
@login_required
@require_role(UserRole.SALES)
def index():
    orders = Order.query.order_by(Order.id.desc()).all()
    return render_template("orders/index.html", orders=orders)


@bp.route("/new", methods=["GET", "POST"])
@login_required
@require_role(UserRole.SALES)
def create():
    if request.method == "POST":
        order = Order(
            client_id=request.form.get("client_id"),
            status=OrderStatus.DRAFT,
            order_date=date.today(),
            created_by_user_id=current_user.id,
        )
        db.session.add(order)
        db.session.commit()
        flash("Order created", "success")
        return redirect(url_for("orders.index"))
    return render_template("orders/new.html")


@bp.route("/<int:order_id>/confirm", methods=["POST"])
@login_required
@require_role(UserRole.SALES)
def confirm(order_id):
    order = Order.query.get_or_404(order_id)
    try:
        order_service.confirm_order(order, current_user)
        db.session.commit()
        flash("Order confirmed", "success")
    except order_service.OrderError as exc:
        db.session.rollback()
        flash(str(exc), "error")
    return redirect(url_for("orders.index"))


@bp.route("/<int:order_id>/lines")
@login_required
@require_role(UserRole.SALES)
def lines_placeholder(order_id):
    return render_template("orders/lines_placeholder.html", order_id=order_id)


@bp.route("/lines/<int:line_id>/assign", methods=["POST"])
@login_required
@require_role(UserRole.SUPERVISOR)
def assign_worker(line_id):
    line = OrderLine.query.get_or_404(line_id)
    worker_id = request.form.get("worker_id")
    try:
        order_service.assign_worker(line, worker_id, current_user)
        db.session.commit()
        flash("Worker assigned", "success")
    except order_service.OrderError as exc:
        db.session.rollback()
        flash(str(exc), "error")
    return redirect(url_for("orders.index"))


@bp.route("/<int:order_id>/change-requests", methods=["GET", "POST"])
@login_required
@require_role(UserRole.SALES)
def change_requests(order_id):
    order = Order.query.get_or_404(order_id)
    if request.method == "POST":
        payload = {"updates": {"notes": request.form.get("notes")}}
        try:
            change_request_service.create_change_request(
                order,
                current_user,
                reason=request.form.get("reason"),
                payload=payload,
            )
            db.session.commit()
            flash("Change request created", "success")
        except change_request_service.ChangeRequestError as exc:
            db.session.rollback()
            flash(str(exc), "error")
        return redirect(url_for("orders.change_requests", order_id=order_id))
    return render_template("orders/change_requests.html", order=order)
