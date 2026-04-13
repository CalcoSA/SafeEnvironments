import time
import hmac
import hashlib
from functools import wraps
from flask import current_app, session, redirect, flash

def validate_wp_access(user: str, ts: str, sig: str) -> bool:
    if not user or not ts or not sig:
        return False

    try:
        ts_int = int(ts)
    except (TypeError, ValueError):
        return False

    max_age = current_app.config.get("ACCESS_MAX_AGE", 300)
    now = int(time.time())

    if abs(now - ts_int) > max_age:
        return False

    secret = current_app.config.get("WP_SHARED_SECRET")
    if not secret:
        return False

    data = f"{user}|{ts}"
    expected_sig = hmac.new(
        secret.encode("utf-8"),
        data.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_sig, sig)

def is_intranet_admin(user: str) -> bool:
    if not user:
        return False

    allowed_users = current_app.config.get("ADMIN_INTRANET_USERS", set())
    return user.strip().lower() in allowed_users

def intranet_only_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("allowed_from_intranet"):
            flash("Debes ingresar a este formulario desde la intranet.", "warning")
            return redirect(current_app.config["INTRANET_URL"])
        return view_func(*args, **kwargs)

    return wrapper

def admin_only_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("allowed_from_intranet"):
            flash("Debes ingresar desde la intranet.", "warning")
            return redirect(current_app.config["INTRANET_URL"])

        if not session.get("can_access_admin", False):
            flash("No tienes permisos para acceder a esta sección.", "danger")
            return redirect(url_for("report.create_form"))

        return view_func(*args, **kwargs)

    return wrapper