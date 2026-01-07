from sqlalchemy import func

from app.extensions import db
from app.models import PayrollLine, PayrollRun, ProductionEntry
from app.models.enums import ProductionStatus
from app.services.audit import log_action


def generate_payroll_run(period_start, period_end, actor_user):
    payroll_run = PayrollRun(
        period_start=period_start,
        period_end=period_end,
        created_by_user_id=actor_user.id,
    )
    db.session.add(payroll_run)
    db.session.flush()

    rows = (
        db.session.query(
            ProductionEntry.worker_id,
            func.coalesce(func.sum(ProductionEntry.qty_done), 0).label("pieces"),
            func.coalesce(func.sum(ProductionEntry.qty_done * ProductionEntry.order_line.unit_rate), 0).label("amount"),
        )
        .join(ProductionEntry.order_line)
        .filter(
            ProductionEntry.status == ProductionStatus.VALIDATED,
            ProductionEntry.entry_date.between(period_start, period_end),
        )
        .group_by(ProductionEntry.worker_id)
        .all()
    )

    for row in rows:
        line = PayrollLine(
            payroll_run_id=payroll_run.id,
            worker_id=row.worker_id,
            pieces_count=row.pieces,
            amount=row.amount,
        )
        db.session.add(line)

    log_action(
        entity_type="PayrollRun",
        entity_id=payroll_run.id,
        action="GENERATED",
        actor_user_id=actor_user.id,
        details={"period_start": str(period_start), "period_end": str(period_end)},
    )
    return payroll_run
