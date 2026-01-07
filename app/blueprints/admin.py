from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import ChangeRequest
from app.models.enums import ChangeRequestStatus, UserRole
from app.services import change_requests as change_request_service
from app.services.authz import require_role


bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/change-requests")
@login_required
@require_role(UserRole.ADMIN)
def change_requests():
    pending = ChangeRequest.query.filter_by(status=ChangeRequestStatus.PENDING).all()
    return render_template("admin/change_requests.html", requests=pending)


@bp.route("/change-requests/<int:request_id>/decide", methods=["POST"])
@login_required
@require_role(UserRole.ADMIN)
def decide_change_request(request_id):
    change_request = ChangeRequest.query.get_or_404(request_id)
    approved = request.form.get("decision") == "approve"
    try:
        change_request_service.decide_change_request(change_request, current_user, approved)
        db.session.commit()
        flash("Change request updated", "success")
    except change_request_service.ChangeRequestError as exc:
        db.session.rollback()
        flash(str(exc), "error")
    return redirect(url_for("admin.change_requests"))
