from flask import current_app
from flask_mail import Message
from app.extensions import mail

class MailService:
    @staticmethod
    def send_email(to, subject, html_body, text_body=None, attachments=None):
        if not to:
            current_app.logger.error("MailService.send_email: no se especificó destinatario")
            raise Exception("No se especificó destinatario para el correo")

        recipients = to if isinstance(to, list) else [to]

        current_app.logger.info(
            "MailService.send_email: iniciando envío | subject=%s | recipients=%s | attachments=%s",
            subject,
            recipients,
            len(attachments or [])
        )

        try:
            msg = Message(subject=subject, recipients=recipients)

            if text_body:
                msg.body = text_body

            msg.html = html_body

            for attachment in attachments or []:
                current_app.logger.info(
                    "MailService.send_email: adjuntando archivo | filename=%s | content_type=%s | size_bytes=%s",
                    attachment.get("filename"),
                    attachment.get("content_type"),
                    len(attachment.get("data", b"")) if attachment.get("data") else 0
                )

                msg.attach(
                    filename=attachment["filename"],
                    content_type=attachment["content_type"],
                    data=attachment["data"]
                )

            current_app.logger.info(
                "MailService.send_email: enviando correo | subject=%s | recipients=%s",
                subject,
                recipients
            )

            mail.send(msg)

            current_app.logger.info(
                "MailService.send_email: correo enviado correctamente | subject=%s | recipients=%s",
                subject,
                recipients
            )

        except Exception as e:
            current_app.logger.exception(
                "MailService.send_email: error enviando correo | subject=%s | recipients=%s | error=%s",
                subject,
                recipients,
                str(e)
            )
            raise