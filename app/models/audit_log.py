from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String

from app.extensions import db
class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    entity_type = Column(String(40), nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(String(60), nullable=False)
    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    details_json = Column(JSON)
    created_at = Column(DateTime, nullable=False)

    actor = db.relationship("User")
