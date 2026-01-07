from functools import wraps

from flask import abort
from flask_login import current_user

from app.models.enums import UserRole


ROLE_ORDER = {
    UserRole.SALES: 1,
    UserRole.SUPERVISOR: 2,
    UserRole.ADMIN: 3,
}


def require_role(min_role: UserRole):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if ROLE_ORDER.get(current_user.role, 0) < ROLE_ORDER[min_role]:
                abort(403)
            return func(*args, **kwargs)

        return wrapper

    return decorator
