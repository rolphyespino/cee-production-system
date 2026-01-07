from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Quote
from app.models.enums import QuoteStatus, UserRole
from app.services.authz import require_role


bp = Blueprint("quotes", __name__, url_prefix="/quotes")


@bp.route("/")
@login_required
@require_role(UserRole.SALES)
def index():
    quotes = Quote.query.order_by(Quote.id.desc()).all()
    return render_template("quotes/index.html", quotes=quotes)


@bp.route("/new", methods=["GET", "POST"])
@login_required
@require_role(UserRole.SALES)
def create():
    if request.method == "POST":
        quote = Quote(
            client_id=request.form.get("client_id"),
            status=QuoteStatus.DRAFT,
            notes=request.form.get("notes"),
            created_by_user_id=current_user.id,
        )
        db.session.add(quote)
        db.session.commit()
        flash("Quote created", "success")
        return redirect(url_for("quotes.index"))
    return render_template("quotes/new.html")


@bp.route("/<int:quote_id>/lines")
@login_required
@require_role(UserRole.SALES)
def lines_placeholder(quote_id):
    return render_template("quotes/lines_placeholder.html", quote_id=quote_id)
