from datetime import datetime

from app.extensions import db
from app.models import AuditLog


def log_action(*, entity_type, entity_id, action, actor_user_id, details=None):
    entry = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor_user_id=actor_user_id,
        details_json=details,
        created_at=datetime.utcnow(),
    )
    db.session.add(entry)
    return entry
