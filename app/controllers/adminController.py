from app.services.accessControl import admin_only_required, parameters_only_required, users_only_required
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.systemParameterService import SystemParameterService
from app.services.catalogService import CatalogService
from app.services.reportService import ReportService
from app.services.userService import UserService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/reports")
@admin_only_required
def reports():
    status = request.args.get("status", "").strip() or None
    page = request.args.get("page", 1, type=int)

    pagination = ReportService.get_all_reports(status=status, page=page, per_page=10)

    return render_template("admin/reports.html", reports=pagination.items, pagination=pagination, selected_status=status)

@admin_bp.route("/catalogs")
@admin_only_required
def catalogs():
    behaviors = CatalogService.get_behaviors()
    impacts = CatalogService.get_impacts()
    return render_template("admin/catalogs.html", behaviors=behaviors, impacts=impacts)

@admin_bp.route("/catalogs/behaviors/create", methods=["POST"])
@admin_only_required
def create_behavior():
    name = request.form.get("name", "")
    success, message, behavior = CatalogService.create_behavior(name)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin.catalogs"))

@admin_bp.route("/catalogs/behaviors/<int:behavior_id>/delete", methods=["POST"])
@admin_only_required
def delete_behavior(behavior_id):
    success, message = CatalogService.delete_behavior(behavior_id)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin.catalogs"))

@admin_bp.route("/catalogs/impacts/create", methods=["POST"])
@admin_only_required
def create_impact():
    name = request.form.get("name", "")
    success, message, impact = CatalogService.create_impact(name)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin.catalogs"))

@admin_bp.route("/catalogs/impacts/<int:impact_id>/delete", methods=["POST"])
@parameters_only_required
def delete_impact(impact_id):
    success, message = CatalogService.delete_impact(impact_id)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin.catalogs"))

@admin_bp.route("/users")
@users_only_required
def users():
    users = UserService.get_all_users()
    return render_template("admin/users.html", users=users)

@admin_bp.route("/users/create", methods=["POST"])
@users_only_required
def create_user():
    try:
        UserService.create_user(request.form)
        flash("Usuario creado correctamente.", "success")
    except Exception as e:
        flash(f"Ocurrió un error al crear el usuario: {str(e)}", "danger")

    return redirect(url_for("admin.users"))

@admin_bp.route("/users/<int:user_id>/update", methods=["POST"])
@users_only_required
def update_user(user_id):
    try:
        UserService.update_user(user_id, request.form)
        flash("Usuario actualizado correctamente.", "success")
    except Exception as e:
        flash(f"Ocurrió un error al actualizar el usuario: {str(e)}", "danger")

    return redirect(url_for("admin.users"))

@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@users_only_required
def delete_user(user_id):
    try:
        UserService.delete_user(user_id)
        flash("Usuario eliminado correctamente.", "success")
    except Exception as e:
        flash(f"Ocurrió un error al eliminar el usuario: {str(e)}", "danger")

    return redirect(url_for("admin.users"))

@admin_bp.route("/parameters")
@parameters_only_required
def parameters():
    parameters = SystemParameterService.get_all_parameters()
    return render_template("admin/parameters.html", parameters=parameters)

@admin_bp.route("/parameters/create", methods=["POST"])
@parameters_only_required
def create_parameter():
    try:
        SystemParameterService.create_parameter(request.form)
        flash("Parámetro creado correctamente.", "success")
    except Exception as e:
        flash(f"Ocurrió un error al crear el parámetro: {str(e)}", "danger")

    return redirect(url_for("admin.parameters"))

@admin_bp.route("/parameters/<int:parameter_id>/update", methods=["POST"])
@parameters_only_required
def update_parameter(parameter_id):
    try:
        SystemParameterService.update_parameter(parameter_id, request.form)
        flash("Parámetro actualizado correctamente.", "success")
    except Exception as e:
        flash(f"Ocurrió un error al actualizar el parámetro: {str(e)}", "danger")

    return redirect(url_for("admin.parameters"))

@admin_bp.route("/parameters/<int:parameter_id>/delete", methods=["POST"])
@parameters_only_required
def delete_parameter(parameter_id):
    try:
        SystemParameterService.delete_parameter(parameter_id)
        flash("Parámetro eliminado correctamente.", "success")
    except Exception as e:
        flash(f"Ocurrió un error al eliminar el parámetro: {str(e)}", "danger")

    return redirect(url_for("admin.parameters"))