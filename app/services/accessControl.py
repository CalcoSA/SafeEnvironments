import time
import hmac
import hashlib
from functools import wraps
from flask import current_app, session, redirect, flash, url_for
from app.domain.repositories.userRepository import UserRepository

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

def get_intranet_user_access(user_login: str) -> dict:
    result = {
        "exists": False,
        "role": None,
        "can_access_admin": False,
        "can_manage_parameters": False,
        "can_manage_users": False,
    }

    if not user_login:
        return result

    user = UserRepository.get_by_user_login(user_login)

    if not user:
        return result

    result["exists"] = True
    result["role"] = user.role

    if user.role == "admin":
        result["can_access_admin"] = True
        result["can_manage_parameters"] = True
        result["can_manage_users"] = True
    elif user.role == "user":
        result["can_access_admin"] = True
        result["can_manage_parameters"] = False
        result["can_manage_users"] = False

    return result

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
            flash("Debes ingresar a este formulario desde la intranet.", "warning")
            return redirect(current_app.config["INTRANET_URL"])

        if not session.get("can_access_admin", False):
            flash("No tienes permisos para acceder a esta sección.", "danger")
            return redirect(url_for("report.create_form"))

        return view_func(*args, **kwargs)

    return wrapper

def parameters_only_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("allowed_from_intranet"):
            flash("Debes ingresar desde la intranet.", "warning")
            return redirect(current_app.config["INTRANET_URL"])

        if not session.get("can_manage_parameters", False):
            flash("No tienes permisos para acceder a parámetros.", "danger")
            return redirect(url_for("admin.reports"))

        return view_func(*args, **kwargs)
    return wrapper

def users_only_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("allowed_from_intranet"):
            flash("Debes ingresar desde la intranet.", "warning")
            return redirect(current_app.config["INTRANET_URL"])

        if not session.get("can_manage_users", False):
            flash("No tienes permisos para acceder a usuarios.", "danger")
            return redirect(url_for("admin.reports"))

        return view_func(*args, **kwargs)
    return wrapper