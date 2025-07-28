# decorators.py

from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
from flask import redirect, url_for, flash
from flask_login import current_user
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access only.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated_function


def head_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_head_admin:
            flash("Access denied. Head Admins only.", "danger")
            return redirect(url_for("admin.admin_dashboard"))
        return f(*args, **kwargs)
    return decorated_function