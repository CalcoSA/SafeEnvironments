from app.extensions import db
from flask import current_app
from app.domain.repositories.systemParameterRepository import SystemParameterRepository

class SystemParameterService:
    CASE_NOTIFICATION_EMAILS_KEY = "CASE_NOTIFICATION_EMAILS"

    @staticmethod
    def get_all_parameters():
        return SystemParameterRepository.get_all()

    @staticmethod
    def get_parameter(parameter_id: int):
        return SystemParameterRepository.get_by_id(parameter_id)

    @staticmethod
    def get_parameter_by_key(key: str):
        return SystemParameterRepository.get_by_key(key)

    @staticmethod
    def create_parameter(form_data: dict):
        try:
            key = (form_data.get("key") or "").strip().upper()
            value = (form_data.get("value") or "").strip()
            description = (form_data.get("description") or "").strip() or None

            if not key:
                raise Exception("La clave del parámetro es obligatoria")

            existing = SystemParameterRepository.get_by_key(key)
            if existing:
                raise Exception("Ya existe un parámetro con esa clave")

            parameter = SystemParameterRepository.create({
                "key": key,
                "value": value or None,
                "description": description
            })

            db.session.commit()
            return parameter

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def update_parameter(parameter_id: int, form_data: dict):
        try:
            parameter = SystemParameterRepository.get_by_id(parameter_id)
            if not parameter:
                raise Exception("Parámetro no encontrado")

            key = (form_data.get("key") or "").strip().upper()
            value = (form_data.get("value") or "").strip()
            description = (form_data.get("description") or "").strip() or None

            if not key:
                raise Exception("La clave del parámetro es obligatoria")

            existing = SystemParameterRepository.get_by_key(key)
            if existing and existing.id != parameter.id:
                raise Exception("Ya existe otro parámetro con esa clave")

            updated = SystemParameterRepository.update(parameter, {
                "key": key,
                "value": value or None,
                "description": description
            })

            db.session.commit()
            return updated

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def delete_parameter(parameter_id: int):
        try:
            parameter = SystemParameterRepository.get_by_id(parameter_id)
            if not parameter:
                raise Exception("Parámetro no encontrado")

            SystemParameterRepository.delete(parameter)
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def get_case_notification_emails():
        parameter = SystemParameterRepository.get_by_key(
            SystemParameterService.CASE_NOTIFICATION_EMAILS_KEY
        )

        raw_value = None

        if parameter and parameter.value:
            raw_value = parameter.value
        else:
            fallback = current_app.config.get("CASE_NOTIFICATION_EMAILS", [])
            if isinstance(fallback, list):
                return [email.strip() for email in fallback if email and email.strip()]
            raw_value = fallback or ""

        return [
            email.strip()
            for email in str(raw_value).split(",")
            if email.strip()
        ]

    @staticmethod
    def ensure_default_parameters():
        existing = SystemParameterRepository.get_by_key(
            SystemParameterService.CASE_NOTIFICATION_EMAILS_KEY
        )
        if existing:
            return

        fallback = current_app.config.get("CASE_NOTIFICATION_EMAILS", [])
        value = ", ".join(fallback) if isinstance(fallback, list) else str(fallback or "")

        SystemParameterRepository.create({
            "key": SystemParameterService.CASE_NOTIFICATION_EMAILS_KEY,
            "value": value,
            "description": "Correos que reciben notificación de nuevos reportes, separados por comas"
        })
        db.session.commit()