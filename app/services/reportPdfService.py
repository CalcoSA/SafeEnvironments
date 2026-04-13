import os
from io import BytesIO
from pathlib import Path
from weasyprint import HTML
from flask import current_app, render_template
from app.services.reportService import ReportService

class ReportPdfService:
    RELATION_LABELS = {
        "jefe_directo": "Jefe/a directo/a",
        "companero": "Compañero/a",
        "persona_a_cargo": "Persona a cargo",
        "proveedor": "Proveedor/a",
        "cliente": "Cliente",
        "otro": "Otro",
    }
    FREQUENCY_LABELS = {
        "una_vez": "Una sola vez",
        "mas_de_una_vez": "Más de una vez",
        "reiterada": "De manera reiterada",
    }
    EVIDENCE_LABELS = {
        "si": "Sí",
        "no": "No",
        "investigar_sin_pruebas": "No tengo pruebas pero deseo que se investigue",
    }
    CURRENT_RISK_LABELS = {
        "si": "Sí",
        "no": "No",
        "no_segura": "No estoy segura",
    }
    PSYCHOLOGICAL_SUPPORT_LABELS = {
        "prioritario": "Sí, lo necesito de manera prioritaria",
        "orientacion": "Sí, me gustaría recibir orientación",
        "no": "No por ahora",
        "mas_informacion": "Necesito más información sobre este apoyo",
    }
    STATUS_LABELS = {
        "nuevo": "Nuevo",
        "en_proceso": "Activo",
        "finalizado": "Inactivo",
    }

    @staticmethod
    def generate_report_pdf(report_id: int):
        report = ReportService.get_report(report_id)

        if not report:
            raise Exception("Reporte no encontrado")

        image_evidences = []
        file_evidences = []

        for evidence in report.evidences or []:
            mime = (evidence.mime_type or "").lower()
            file_path = evidence.file_path

            if file_path and os.path.exists(file_path) and mime.startswith("image/"):
                image_evidences.append({
                    "file_name": evidence.file_name,
                    "file_uri": Path(file_path).resolve().as_uri(),
                    "mime_type": evidence.mime_type,
                })
            else:
                file_evidences.append({
                    "file_name": evidence.file_name,
                    "mime_type": evidence.mime_type,
                })

        logo_path = Path(current_app.root_path) / "static" / "img" / "TextoCrepes.png"
        logo_uri = logo_path.resolve().as_uri() if logo_path.exists() else None

        html = render_template(
            "admin/pdf.html",
            report=report,
            image_evidences=image_evidences,
            file_evidences=file_evidences,
            relation_labels=ReportPdfService.RELATION_LABELS,
            frequency_labels=ReportPdfService.FREQUENCY_LABELS,
            evidence_labels=ReportPdfService.EVIDENCE_LABELS,
            current_risk_labels=ReportPdfService.CURRENT_RISK_LABELS,
            psychological_support_labels=ReportPdfService.PSYCHOLOGICAL_SUPPORT_LABELS,
            status_labels=ReportPdfService.STATUS_LABELS,
            logo_uri=logo_uri,
        )

        pdf_bytes = HTML(
            string=html,
            base_url=str(Path.cwd())
        ).write_pdf()

        pdf_buffer = BytesIO(pdf_bytes)
        pdf_buffer.seek(0)

        return {
            "report": report,
            "file_buffer": pdf_buffer,
            "file_name": f"reporte_{report.id}.pdf",
        }