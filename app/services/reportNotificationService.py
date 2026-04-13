from flask import current_app
from app.services.mailService import MailService
from app.services.reportPdfService import ReportPdfService

class ReportNotificationService:
    @staticmethod
    def send_report_created_notifications(report):
        pdf_data = ReportPdfService.generate_report_pdf(report.id)
        pdf_bytes = pdf_data["file_buffer"].getvalue()

        attachment = {
            "filename": pdf_data["file_name"],
            "content_type": "application/pdf",
            "data": pdf_bytes,
        }

        reporter_email = report.reporter_user.email if report.reporter_user else None
        committee_emails = current_app.config.get("CASE_NOTIFICATION_EMAILS", [])

        if reporter_email:
            MailService.send_email(
                to=reporter_email,
                subject=f"Confirmación de recepción del reporte #{report.id}",
                text_body=(
                    f"Tu reporte #{report.id} fue recibido correctamente. "
                    "Adjunto encontrarás una copia en PDF."
                ),
                html_body=ReportNotificationService._build_reporter_email(report),
                attachments=[attachment]
            )

        if committee_emails:
            MailService.send_email(
                to=committee_emails,
                subject=f"Nuevo reporte registrado #{report.id}",
                text_body=(
                    f"Se registró un nuevo reporte #{report.id}. "
                    "Adjunto se envía el PDF del caso."
                ),
                html_body=ReportNotificationService._build_committee_email(report),
                attachments=[attachment]
            )

    @staticmethod
    def _build_reporter_email(report):
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #513629;">Confirmación de recepción del reporte</h2>
                <p>Hola <strong>{report.reporter_name}</strong>,</p>
                <p>Hemos recibido correctamente tu reporte con consecutivo <strong>#{report.id}</strong>.</p>
                <p>La información será tratada de manera confidencial y revisada por el equipo encargado.</p>
                <p>Adjunto encontrarás una copia del reporte en PDF.</p>
                <br>
                <p><strong>Canal Confidencial</strong></p>
            </body>
        </html>
        """

    @staticmethod
    def _build_committee_email(report):
        reporter_email = report.reporter_user.email if report.reporter_user and report.reporter_user.email else "No informado"

        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #513629;">Nuevo reporte registrado</h2>
                <p>Se ha registrado un nuevo reporte en el sistema.</p>
                <ul>
                    <li><strong>Consecutivo:</strong> #{report.id}</li>
                    <li><strong>Reportante:</strong> {report.reporter_name}</li>
                    <li><strong>Correo reportante:</strong> {reporter_email}</li>
                    <li><strong>Persona señalada:</strong> {report.accused_name}</li>
                    <li><strong>Estado:</strong> {report.status}</li>
                </ul>
                <p>Adjunto se envía el PDF del caso para revisión.</p>
                <br>
                <p><strong>Canal Confidencial</strong></p>
            </body>
        </html>
        """