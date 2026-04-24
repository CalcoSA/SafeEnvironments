import os
import uuid
import pytz
from flask import current_app
from app.extensions import db
from datetime import datetime
from app.domain.models.user import User
from werkzeug.utils import secure_filename
from app.domain.repositories.userRepository import UserRepository
from app.domain.repositories.reportRepository import ReportRepository
from app.domain.repositories.impactRepository import ImpactRepository
from app.domain.repositories.behaviorRepository import BehaviorRepository
from app.domain.repositories.evidenceRepository import EvidenceRepository
from app.domain.repositories.reportHistoryRepository import ReportHistoryRepository

class ReportService:
    FREQUENCY_MAP = {
        "Una sola vez": "una_vez",
        "Más de una vez": "mas_de_una_vez",
        "De manera reiterada": "reiterada",
    }
    EVIDENCE_MAP = {
        "Sí": "si",
        "No": "no",
        "No tengo pruebas pero deseo que se investigue": "investigar_sin_pruebas",
    }
    CURRENT_RISK_MAP = {
        "Sí": "si",
        "No": "no",
        "No estoy segura": "no_segura",
        "No estoy seguro/a": "no_segura",
    }
    PSYCHOLOGICAL_SUPPORT_MAP = {
        "Sí, lo necesito de manera prioritaria": "prioritario",
        "Sí, me gustaría recibir orientación": "orientacion",
        "No por ahora": "no",
        "Necesito más información sobre este apoyo": "mas_informacion",
    }
    RELATION_MAP = {
        "Jefe/a directo/a": "jefe_directo",
        "Compañero/a": "companero",
        "Persona a cargo": "persona_a_cargo",
        "Proveedor/a": "proveedor",
        "Cliente": "cliente",
        "Otro": "otro",
    }
    STATUS_LABEL_TO_VALUE = {
        "Nuevo": "nuevo",
        "Activo": "en_proceso",
        "Inactivo": "finalizado",
        "Archivado": "archivado",
    }

    @staticmethod
    def get_all_reports(status=None, page=1, per_page=10):
        return ReportRepository.get_all(status=status, page=page, per_page=per_page)

    @staticmethod
    def get_report(report_id: int):
        return ReportRepository.get_by_id(report_id)

    @staticmethod
    def create_report(form_data: dict, files: list):
        try:
            behavior_ids = form_data.get("behavior_ids", [])

            if not behavior_ids:
                raise Exception("Debes seleccionar al menos una conducta")

            impact_ids = form_data.get("impact_ids", [])

            if not impact_ids:
                raise Exception("Debes seleccionar al menos un impacto")

            normalized_frequency = ReportService.FREQUENCY_MAP.get(form_data.get("occurrence_frequency"))

            if not normalized_frequency:
                raise Exception("La frecuencia seleccionada no es válida")

            normalized_has_evidence = ReportService.EVIDENCE_MAP.get(form_data.get("has_evidence"))

            if not normalized_has_evidence:
                raise Exception("La opción de pruebas no es válida")

            normalized_current_risk = ReportService.CURRENT_RISK_MAP.get(form_data.get("current_risk"))

            if not normalized_current_risk:
                raise Exception("La opción de seguridad actual no es válida")

            normalized_psychological_support = ReportService.PSYCHOLOGICAL_SUPPORT_MAP.get(form_data.get("psychological_support"))

            if not normalized_psychological_support:
                raise Exception("La opción de acompañamiento psicológico no es válida")

            normalized_relation = ReportService.RELATION_MAP.get(form_data.get("relationship_type"))

            if not normalized_relation:
                raise Exception("La relación con la persona señalada no es válida")
            
            relationship_type_other = (form_data.get("relationship_type_other") or "").strip()

            if normalized_relation == "otro" and not relationship_type_other:
                raise Exception("Debes especificar la relación cuando seleccionas 'Otro'")

            valid_files = [f for f in (files or []) if f and f.filename]

            if normalized_has_evidence == "si" and not valid_files:
                raise Exception("Debes adjuntar al menos una evidencia si seleccionas 'Sí'")

            reporter_data = {
                "name": form_data.get("reporter_full_name"),
                "document": form_data.get("reporter_document_number"),
                "email": form_data.get("reporter_email"),
                "phone": form_data.get("reporter_phone_number"),
                "role": "reporter",
                "area": form_data.get("reporter_point_of_sale_area"),
                "position": form_data.get("reporter_current_position"),
            }

            reporter_success, reporter_message, reporter_user = UserRepository.create_or_update_by_document(reporter_data)

            if not reporter_success:
                raise Exception(reporter_message)

            accused_name = (form_data.get("involved_person_name") or "").strip()
            accused_position = (form_data.get("involved_person_position") or "").strip()
            accused_area = (form_data.get("involved_person_point_of_sale") or "").strip()

            if not accused_name:
                raise Exception("El nombre de la persona involucrada es obligatorio")

            accused_user = None

            accused_user = User.query.filter(db.func.lower(User.name) == accused_name.lower()).first()

            if accused_user:
                accused_user = UserRepository.update(accused_user, {
                    "name": accused_name,
                    "position": accused_position or accused_user.position,
                    "area": accused_area or accused_user.area,
                })
            else:
                accused_user = UserRepository.create({
                    "name": accused_name,
                    "document": None,
                    "email": None,
                    "phone": None,
                    "role": "reporter",
                    "area": accused_area or None,
                    "position": accused_position or None,
                })

            report_data = {
                "reporter_user_id": reporter_user.id,
                "accused_user_id": accused_user.id,
                "reporter_name": reporter_user.name,
                "reporter_area": form_data.get("reporter_point_of_sale_area"),
                "reporter_position": form_data.get("reporter_current_position"),
                "accused_name": accused_name,
                "accused_area": accused_area,
                "accused_position": accused_position,
                "narrative": form_data.get("facts_description"),
                "accused_relation": normalized_relation,
                "accused_relation_other": relationship_type_other if normalized_relation == "otro" else None,
                "frequency": normalized_frequency,
                "has_evidence": normalized_has_evidence,
                "current_risk": normalized_current_risk,
                "psychological_support": normalized_psychological_support,
                "status": "nuevo",
                "closed_at": None,
            }

            report = ReportRepository.create(report_data)

            ReportHistoryRepository.create({
                "report_id": report.id,
                "status": "nuevo",
                "comment": "Reporte creado exitosamente.",
                "changed_by_user_login": None,
            })

            BehaviorRepository.link_behaviors(report.id, behavior_ids)
            ImpactRepository.link_impacts(report.id, impact_ids)

            if normalized_has_evidence == "si":
                ReportService._save_evidences(report.id, valid_files)

            db.session.commit()

            try:
                from app.services.reportNotificationService import ReportNotificationService
                
                ReportNotificationService.send_report_created_notifications(report)
            except Exception as mail_error:
                current_app.logger.error(
                    f"Error enviando notificaciones del reporte {report.id}: {mail_error}"
                )

            return report

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def _save_evidences(report_id: int, files: list):
        if not files:
            return []

        upload_root = current_app.config.get("EVIDENCE_UPLOAD_DIR")
        if not upload_root:
            upload_root = os.path.join("private_storage", "evidencias")

        upload_root = os.path.abspath(str(upload_root))
        report_folder = os.path.abspath(os.path.join(upload_root, f"report_{report_id}"))
        os.makedirs(report_folder, exist_ok=True)

        evidence_items = []

        for file in files:
            if not file or not file.filename:
                continue

            original_filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
            full_path = os.path.abspath(os.path.join(report_folder, unique_filename))

            file.save(full_path)

            evidence_items.append({
                "report_id": report_id,
                "file_name": original_filename,
                "file_path": full_path,
                "mime_type": file.mimetype,
            })

        return EvidenceRepository.create_many(evidence_items)

    @staticmethod
    def update_report_status(report_id: int, new_status: str, comment: str = None, changed_by_user_login: str = None):
        try:
            report = ReportRepository.get_by_id(report_id)

            if not report:
                raise Exception("Reporte no encontrado")

            allowed_statuses = ["nuevo", "en_proceso", "finalizado", "archivado"]

            if new_status not in allowed_statuses:
                raise Exception("El estado seleccionado no es válido")

            if report.status == "archivado":
                raise Exception("El reporte ya está archivado y no puede volver a actualizarse")

            if report.status == "finalizado" and new_status != "archivado":
                raise Exception("El reporte finalizado solo puede pasar a archivado")

            comment = (comment or "").strip()
            if not comment:
                raise Exception("Debes ingresar un comentario para registrar el cambio de estado")

            data_to_update = {
                "status": new_status
            }

            if new_status == "finalizado":
                data_to_update["closed_at"] = datetime.now(
                    pytz.timezone("America/Bogota")
                ).replace(tzinfo=None)
            elif new_status in ["nuevo", "en_proceso"]:
                data_to_update["closed_at"] = None

            updated_report = ReportRepository.update(report, data_to_update)

            ReportHistoryRepository.create({
                "report_id": report.id,
                "status": new_status,
                "comment": comment,
                "changed_by_user_login": changed_by_user_login,
            })

            db.session.commit()

            try:
                from app.services.reportNotificationService import ReportNotificationService
                ReportNotificationService.send_report_status_changed_notifications(
                    updated_report,
                    changed_by_user_login=changed_by_user_login,
                    comment=comment
                )
            except Exception as mail_error:
                current_app.logger.error(
                    f"Error enviando notificación de cambio de estado del reporte {report.id}: {mail_error}"
                )

            return updated_report

        except Exception:
            db.session.rollback()
            raise
    
    @staticmethod
    def get_evidence(evidence_id: int):
        evidence = EvidenceRepository.get_by_id(evidence_id)

        if not evidence:
            raise Exception("Evidencia no encontrada")

        if not evidence.file_path:
            raise Exception("La evidencia no tiene una ruta válida")

        if not os.path.exists(evidence.file_path):
            raise Exception("El archivo de evidencia no existe en el servidor")

        return evidence

    @staticmethod
    def can_preview_evidence(evidence):
        previewable_mimes = {
            "application/pdf",
            "image/png",
            "image/jpeg",
            "image/jpg",
        }
        return evidence.mime_type in previewable_mimes
    
    @staticmethod
    def create_manual_report(form_data: dict, files: list, created_by_user_login: str = None):
        try:
            reporter_data = {
                "name": (form_data.get("reporter_full_name") or "").strip(),
                "document": (form_data.get("reporter_document_number") or "").strip(),
                "email": (form_data.get("reporter_email") or "").strip(),
                "phone": (form_data.get("reporter_phone_number") or "").strip(),
                "role": "reporter",
                "area": (form_data.get("reporter_point_of_sale_area") or "").strip(),
                "position": (form_data.get("reporter_current_position") or "").strip(),
            }

            required_reporter_fields = {
                "Nombre del reportante": reporter_data["name"],
                "Documento del reportante": reporter_data["document"],
                "Correo del reportante": reporter_data["email"],
                "Teléfono del reportante": reporter_data["phone"],
                "CDS del reportante": reporter_data["area"],
                "Cargo del reportante": reporter_data["position"],
            }

            for label, value in required_reporter_fields.items():
                if not value:
                    raise Exception(f"{label} es obligatorio")

            reporter_success, reporter_message, reporter_user = UserRepository.create_or_update_by_document(reporter_data)

            if not reporter_success:
                raise Exception(reporter_message)

            accused_name = (form_data.get("involved_person_name") or "").strip()
            accused_position = (form_data.get("involved_person_position") or "").strip()
            accused_area = (form_data.get("involved_person_point_of_sale") or "").strip()

            if not accused_name:
                raise Exception("El nombre de la persona involucrada es obligatorio")

            if not accused_position:
                raise Exception("El cargo de la persona involucrada es obligatorio")

            if not accused_area:
                raise Exception("El CDS de la persona involucrada es obligatorio")

            accused_user = User.query.filter(
                db.func.lower(User.name) == accused_name.lower()
            ).first()

            if accused_user:
                accused_user = UserRepository.update(accused_user, {
                    "name": accused_name,
                    "position": accused_position or accused_user.position,
                    "area": accused_area or accused_user.area,
                })
            else:
                accused_user = UserRepository.create({
                    "name": accused_name,
                    "document": None,
                    "email": None,
                    "phone": None,
                    "role": "reporter",
                    "area": accused_area,
                    "position": accused_position,
                })

            valid_files = [f for f in (files or []) if f and f.filename]

            default_has_evidence = "si" if valid_files else "no"

            include_manual_narrative = form_data.get("include_manual_narrative") == "on"
            manual_narrative = (form_data.get("manual_narrative") or "").strip()

            if include_manual_narrative:
                if not manual_narrative:
                    raise Exception("Debes ingresar el relato de los hechos")
                narrative = manual_narrative
            else:
                narrative = "Reporte cargado manualmente por gestor de casos."

            report_data = {
                "reporter_user_id": reporter_user.id,
                "accused_user_id": accused_user.id,
                "reporter_name": reporter_user.name,
                "reporter_area": reporter_data["area"],
                "reporter_position": reporter_data["position"],
                "accused_name": accused_name,
                "accused_area": accused_area,
                "accused_position": accused_position,
                "narrative": narrative,
                "accused_relation": None,
                "accused_relation_other": None,
                "frequency": None,
                "current_risk": None,
                "psychological_support": None,
                "has_evidence": default_has_evidence,
                "status": "nuevo",
                "closed_at": None,
            }

            report = ReportRepository.create(report_data)

            ReportHistoryRepository.create({
                "report_id": report.id,
                "status": "nuevo",
                "comment": "Reporte creado manualmente por gestor de casos.",
                "changed_by_user_login": created_by_user_login,
            })

            if valid_files:
                ReportService._save_evidences(report.id, valid_files)

            db.session.commit()

            try:
                from app.services.reportNotificationService import ReportNotificationService
                ReportNotificationService.send_report_created_notifications(report)
            except Exception as mail_error:
                current_app.logger.error(
                    f"Error enviando notificaciones del reporte manual {report.id}: {mail_error}"
                )

            return report

        except Exception:
            db.session.rollback()
            raise