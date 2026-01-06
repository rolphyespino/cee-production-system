from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from app.extensions import db
from app.models import CatalogItem, PieceRate
from app.models.enums import ItemType, RateType, UserRole
from app.services.authz import require_role


bp = Blueprint("catalog", __name__, url_prefix="/catalog")


@bp.route("/")
@login_required
@require_role(UserRole.SALES)
def index():
    items = CatalogItem.query.order_by(CatalogItem.code).all()
    return render_template("catalog/index.html", items=items)


@bp.route("/new", methods=["GET", "POST"])
@login_required
@require_role(UserRole.SUPERVISOR)
def create():
    if request.method == "POST":
        item = CatalogItem(
            item_type=ItemType(request.form.get("item_type")),
            code=request.form.get("code"),
            name=request.form.get("name"),
        )
        db.session.add(item)
        db.session.commit()
        flash("Catalog item created", "success")
        return redirect(url_for("catalog.index"))
    return render_template("catalog/new.html")


@bp.route("/piece-rates/<int:catalog_item_id>", methods=["GET", "POST"])
@login_required
@require_role(UserRole.SUPERVISOR)
def piece_rates(catalog_item_id):
    item = CatalogItem.query.get_or_404(catalog_item_id)
    if request.method == "POST":
        piece_rate = PieceRate(
            catalog_item_id=item.id,
            rate_type=RateType.CONFECCION,
            rate_amount=request.form.get("rate_amount"),
            effective_from=request.form.get("effective_from"),
            is_active=True,
        )
        db.session.add(piece_rate)
        db.session.commit()
        flash("Piece rate created", "success")
        return redirect(url_for("catalog.index"))
    rates = PieceRate.query.filter_by(catalog_item_id=item.id).all()
    return render_template("catalog/piece_rates.html", item=item, rates=rates)
