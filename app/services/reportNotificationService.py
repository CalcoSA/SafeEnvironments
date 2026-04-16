from flask import current_app
from app.services.mailService import MailService
from app.services.reportPdfService import ReportPdfService
from app.services.systemParameterService import SystemParameterService

class ReportNotificationService:
    @staticmethod
    def send_report_created_notifications(report):
        current_app.logger.info(
            "ReportNotificationService.send_report_created_notifications: inicio | report_id=%s",
            report.id
        )

        try:
            pdf_data = ReportPdfService.generate_report_pdf(report.id)
            pdf_bytes = pdf_data["file_buffer"].getvalue()

            current_app.logger.info(
                "ReportNotificationService: PDF generado correctamente | report_id=%s | file_name=%s | size_bytes=%s",
                report.id,
                pdf_data["file_name"],
                len(pdf_bytes)
            )

            attachment = {
                "filename": pdf_data["file_name"],
                "content_type": "application/pdf",
                "data": pdf_bytes,
            }

            reporter_email = report.reporter_user.email if report.reporter_user else None
            committee_emails = SystemParameterService.get_case_notification_emails()

            current_app.logger.info(
                "ReportNotificationService: destinatarios resueltos | report_id=%s | reporter_email=%s | committee_emails=%s",
                report.id,
                reporter_email,
                committee_emails
            )

            if reporter_email:
                current_app.logger.info(
                    "ReportNotificationService: enviando confirmación al reportante | report_id=%s | email=%s",
                    report.id,
                    reporter_email
                )

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

            else:
                current_app.logger.warning(
                    "ReportNotificationService: no se enviará correo al reportante porque no tiene email | report_id=%s",
                    report.id
                )

            if committee_emails:
                current_app.logger.info(
                    "ReportNotificationService: enviando notificación al comité | report_id=%s | emails=%s",
                    report.id,
                    committee_emails
                )

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

            else:
                current_app.logger.warning(
                    "ReportNotificationService: no se enviará correo al comité porque no hay destinatarios configurados | report_id=%s",
                    report.id
                )

            current_app.logger.info(
                "ReportNotificationService.send_report_created_notifications: fin exitoso | report_id=%s",
                report.id
            )

        except Exception as e:
            current_app.logger.exception(
                "ReportNotificationService.send_report_created_notifications: error | report_id=%s | error=%s",
                report.id,
                str(e)
            )
            raise

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

    @staticmethod
    def send_report_status_changed_notifications(report, changed_by_user_login: str, comment: str):
        current_app.logger.info(
            "ReportNotificationService.send_report_status_changed_notifications: inicio | report_id=%s | changed_by=%s | new_status=%s",
            report.id,
            changed_by_user_login,
            report.status
        )

        try:
            reporter_email = report.reporter_user.email if report.reporter_user else None
            committee_emails = SystemParameterService.get_case_notification_emails()

            status_label = ReportNotificationService._translate_status(report.status)

            if reporter_email:
                current_app.logger.info(
                    "ReportNotificationService: enviando cambio de estado al reportante | report_id=%s | email=%s",
                    report.id,
                    reporter_email
                )

                MailService.send_email(
                    to=reporter_email,
                    subject=f"Actualización del reporte #{report.id}",
                    text_body=(
                        f"El reporte #{report.id} cambió de estado a {status_label}. "
                        f"Comentario: {comment}"
                    ),
                    html_body=ReportNotificationService._build_reporter_status_email(
                        report,
                        changed_by_user_login,
                        comment
                    )
                )
            else:
                current_app.logger.warning(
                    "ReportNotificationService: el reportante no tiene correo | report_id=%s",
                    report.id
                )

            if committee_emails:
                current_app.logger.info(
                    "ReportNotificationService: enviando cambio de estado al comité | report_id=%s | emails=%s",
                    report.id,
                    committee_emails
                )

                MailService.send_email(
                    to=committee_emails,
                    subject=f"Actualización de estado del reporte #{report.id}",
                    text_body=(
                        f"El reporte #{report.id} cambió de estado a {status_label}. "
                        f"Usuario: {changed_by_user_login or 'No informado'}. "
                        f"Comentario: {comment}"
                    ),
                    html_body=ReportNotificationService._build_committee_status_email(
                        report,
                        changed_by_user_login,
                        comment
                    )
                )
            else:
                current_app.logger.warning(
                    "ReportNotificationService: no hay correos configurados para el comité | report_id=%s",
                    report.id
                )

            current_app.logger.info(
                "ReportNotificationService.send_report_status_changed_notifications: fin exitoso | report_id=%s",
                report.id
            )

        except Exception as e:
            current_app.logger.exception(
                "ReportNotificationService.send_report_status_changed_notifications: error | report_id=%s | error=%s",
                report.id,
                str(e)
            )
            raise

    @staticmethod
    def _translate_status(status):
        if status == "nuevo":
            return "Nuevo"
        if status == "en_proceso":
            return "Activo"
        if status == "finalizado":
            return "Inactivo"
        if status == "archivado":
            return "Archivado"
        return status

    @staticmethod
    def _build_reporter_status_email(report, changed_by_user_login, comment):
        status_label = ReportNotificationService._translate_status(report.status)

        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #513629;">Actualización de tu reporte</h2>
                <p>Hola <strong>{report.reporter_name}</strong>,</p>
                <p>Tu reporte con consecutivo <strong>#{report.id}</strong> cambió de estado.</p>
                <ul>
                    <li><strong>Nuevo estado:</strong> {status_label}</li>
                    <li><strong>Comentario:</strong> {comment}</li>
                </ul>
                <br>
                <p><strong>Canal Confidencial</strong></p>
            </body>
        </html>
        """

    @staticmethod
    def _build_committee_status_email(report, changed_by_user_login, comment):
        status_label = ReportNotificationService._translate_status(report.status)

        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #513629;">Cambio de estado de reporte</h2>
                <p>Se actualizó el estado de un reporte.</p>
                <ul>
                    <li><strong>Consecutivo:</strong> #{report.id}</li>
                    <li><strong>Reportante:</strong> {report.reporter_name}</li>
                    <li><strong>Nuevo estado:</strong> {status_label}</li>
                    <li><strong>Usuario que realizó el cambio:</strong> {changed_by_user_login or "No informado"}</li>
                    <li><strong>Comentario:</strong> {comment}</li>
                </ul>
                <br>
                <p><strong>Canal Confidencial</strong></p>
            </body>
        </html>
        """