from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.catalogService import CatalogService
from app.services.reportService import ReportService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/reports")
def reports():
    status = request.args.get("status", "").strip() or None
    page = request.args.get("page", 1, type=int)

    pagination = ReportService.get_all_reports(status=status, page=page, per_page=10)

    return render_template("admin/reports.html", reports=pagination.items, pagination=pagination, selected_status=status)

@admin_bp.route("/catalogs")
def catalogs():
    behaviors = CatalogService.get_behaviors()
    impacts = CatalogService.get_impacts()
    return render_template("admin/catalogs.html", behaviors=behaviors, impacts=impacts)

@admin_bp.route("/catalogs/behaviors/create", methods=["POST"])
def create_behavior():
    name = request.form.get("name", "")
    success, message, behavior = CatalogService.create_behavior(name)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin.catalogs"))

@admin_bp.route("/catalogs/behaviors/<int:behavior_id>/delete", methods=["POST"])
def delete_behavior(behavior_id):
    success, message = CatalogService.delete_behavior(behavior_id)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin.catalogs"))

@admin_bp.route("/catalogs/impacts/create", methods=["POST"])
def create_impact():
    name = request.form.get("name", "")
    success, message, impact = CatalogService.create_impact(name)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin.catalogs"))

@admin_bp.route("/catalogs/impacts/<int:impact_id>/delete", methods=["POST"])
def delete_impact(impact_id):
    success, message = CatalogService.delete_impact(impact_id)
    flash(message, "success" if success else "danger")
    return redirect(url_for("admin.catalogs"))
