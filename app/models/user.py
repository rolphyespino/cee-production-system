from sqlalchemy import Boolean, Column, Enum, Integer, String
from flask_login import UserMixin

from app.extensions import db
from app.models.base import TimestampMixin
from app.models.enums import UserRole


class User(db.Model, UserMixin, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    full_name = Column(String(120), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
