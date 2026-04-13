from app.extensions import db
from sqlalchemy import case, func, exists
from app.domain.models.behavior import Behavior
from app.domain.models.report_behavior import ReportBehavior

class BehaviorRepository:
    @staticmethod
    def get_all():
        return Behavior.query.order_by(
            case((Behavior.name == "Otra", 1), else_=0),
            Behavior.name.asc()
        ).all()

    @staticmethod
    def get_by_ids(ids: list[int]):
        if not ids:
            return []
        return Behavior.query.filter(Behavior.id.in_(ids)).all()

    @staticmethod
    def link_behaviors(report_id: int, behavior_ids: list[int]):
        for behavior_id in behavior_ids:
            db.session.add(
                ReportBehavior(
                    report_id=report_id,
                    behavior_id=behavior_id
                )
            )
        db.session.flush()

    @staticmethod
    def create(name: str):
        normalized_name = " ".join((name or "").strip().split())
        if not normalized_name:
            return False, "El nombre de la conducta es obligatorio", None
        existing = Behavior.query.filter(
            func.lower(Behavior.name) == normalized_name.lower()
        ).first()
        if existing:
            return False, "Ya existe una conducta con ese nombre", None
        behavior = Behavior(name=normalized_name)
        db.session.add(behavior)
        db.session.flush()
        return True, "Conducta creada correctamente", behavior

    @staticmethod
    def delete(behavior_id: int):
        behavior = Behavior.query.get(behavior_id)
        if not behavior:
            return False, "Conducta no encontrada"
        in_use = db.session.query(
            exists().where(ReportBehavior.behavior_id == behavior_id)
        ).scalar()
        if in_use:
            return False, "No se puede eliminar la conducta porque está asociada a uno o más reportes"
        db.session.delete(behavior)
        db.session.flush()
        return True, "Conducta eliminada correctamente"