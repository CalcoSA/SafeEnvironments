from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, session, current_app
from app.services.accessControl import validate_wp_access, intranet_only_required, is_intranet_admin
from app.services.reportPdfService import ReportPdfService
from app.services.catalogService import CatalogService
from app.services.reportService import ReportService
import os

report_bp = Blueprint("report", __name__, url_prefix="/reports")

@report_bp.route("/access", methods=["GET"])
def access():
    user = request.args.get("user")
    ts = request.args.get("ts")
    sig = request.args.get("sig")

    if not user or not ts or not sig:
        return redirect(current_app.config["INTRANET_URL"])

    if not validate_wp_access(user, ts, sig):
        flash("El enlace de acceso no es válido o expiró.", "warning")
        return redirect(current_app.config["INTRANET_URL"])

    session["allowed_from_intranet"] = True
    session["intranet_user"] = user
    session["can_access_admin"] = is_intranet_admin(user)
    session.permanent = True

    return redirect(url_for("report.create_form"))

@report_bp.route("/new", methods=["GET"])
@intranet_only_required
def create_form():
    behaviors = CatalogService.get_behaviors()
    impacts = CatalogService.get_impacts()

    return render_template(
        "reports/create.html",
        behaviors=behaviors,
        impacts=impacts
    )

@report_bp.route("/", methods=["POST"])
@intranet_only_required
def store():
    try:
        behavior_ids = [int(x) for x in request.form.getlist("behavior_ids")]
        impact_ids = [int(x) for x in request.form.getlist("impact_ids")]
        files = request.files.getlist("evidence_files")

        form_data = {
            "reporter_full_name": request.form.get("reporter_full_name"),
            "reporter_document_number": request.form.get("reporter_document_number"),
            "reporter_point_of_sale_area": request.form.get("reporter_point_of_sale_area"),
            "reporter_current_position": request.form.get("reporter_current_position"),
            "reporter_email": request.form.get("reporter_email"),
            "reporter_phone_number": request.form.get("reporter_phone_number"),

            "involved_person_name": request.form.get("involved_person_name"),
            "involved_person_position": request.form.get("involved_person_position"),
            "involved_person_point_of_sale": request.form.get("involved_person_point_of_sale"),
            "relationship_type": request.form.get("relationship_type"),
            "relationship_type_other": request.form.get("relationship_type_other"),

            "facts_description": request.form.get("facts_description"),
            "occurrence_frequency": request.form.get("occurrence_frequency"),
            "has_evidence": request.form.get("has_evidence"),
            "current_risk": request.form.get("current_risk"),
            "psychological_support": request.form.get("psychological_support"),

            "behavior_ids": behavior_ids,
            "impact_ids": impact_ids,
        }

        report = ReportService.create_report(form_data, files)

        flash("El reporte fue registrado correctamente.", "success")
        return redirect(url_for("report.create_form"))

    except Exception as e:
        flash(f"Ocurrió un error al registrar el reporte: {str(e)}", "danger")
        return redirect(url_for("report.create_form"))

@report_bp.route("/<int:report_id>", methods=["GET"])
def show(report_id):
    report = ReportService.get_report(report_id)

    if not report:
        flash("Reporte no encontrado.", "warning")
        return redirect(url_for("report.create_form"))

    return render_template("reports/show.html", report=report)

@report_bp.route("/<int:report_id>/status", methods=["POST"])
def update_status(report_id):
    try:
        new_status = request.form.get("status")
        ReportService.update_report_status(report_id, new_status)

        flash("El estado del reporte fue actualizado correctamente.", "success")
        return redirect(url_for("admin.reports"))

    except Exception as e:
        flash(f"Ocurrió un error al actualizar el estado: {str(e)}", "danger")
        return redirect(url_for("admin.reports"))

@report_bp.route("/evidences/<int:evidence_id>/view", methods=["GET"])
def view_evidence(evidence_id):
    try:
        evidence = ReportService.get_evidence(evidence_id)

        return send_file(
            evidence.file_path,
            mimetype=evidence.mime_type,
            as_attachment=False,
            download_name=evidence.file_name
        )

    except Exception as e:
        flash(f"No fue posible visualizar la evidencia: {str(e)}", "danger")
        return redirect(url_for("admin.reports"))


@report_bp.route("/evidences/<int:evidence_id>/download", methods=["GET"])
def download_evidence(evidence_id):
    try:
        evidence = ReportService.get_evidence(evidence_id)

        return send_file(
            evidence.file_path,
            mimetype=evidence.mime_type,
            as_attachment=True,
            download_name=evidence.file_name
        )

    except Exception as e:
        flash(f"No fue posible descargar la evidencia: {str(e)}", "danger")
        return redirect(url_for("admin.reports"))

@report_bp.route("/<int:report_id>/pdf", methods=["GET"])
def export_pdf(report_id):
    try:
        pdf_data = ReportPdfService.generate_report_pdf(report_id)

        return send_file(pdf_data["file_buffer"], mimetype="application/pdf", as_attachment=True, download_name=pdf_data["file_name"] )

    except Exception as e:
        flash(f"No fue posible generar el PDF: {str(e)}", "danger")
        return redirect(url_for("admin.reports"))

@report_bp.route("/exit", methods=["GET"])
def exit_form():
    session.pop("allowed_from_intranet", None)
    session.pop("intranet_user", None)
    return redirect(current_app.config["INTRANET_URL"])