from flask import current_app
from flask_mail import Message
from app.extensions import mail

class MailService:
    @staticmethod
    def send_email(to, subject, html_body, text_body=None, attachments=None):
        if not to:
            raise Exception("No se especificó destinatario para el correo")

        recipients = to if isinstance(to, list) else [to]

        msg = Message(
            subject=subject,
            recipients=recipients
        )

        if text_body:
            msg.body = text_body

        msg.html = html_body

        for attachment in attachments or []:
            msg.attach(
                filename=attachment["filename"],
                content_type=attachment["content_type"],
                data=attachment["data"]
            )

        mail.send(msg)