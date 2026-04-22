from app.extensions import db
from sqlalchemy import func, case
from app.domain.models.impact import Impact
from app.domain.models.report_impact import ReportImpact

class ImpactRepository:
    @staticmethod
    def get_all():
        return Impact.query.order_by(
            case((Impact.name == "Otro", 1), else_=0),
            Impact.name.asc()
        ).all()

    @staticmethod
    def get_by_ids(ids: list[int]):
        if not ids:
            return []
        return Impact.query.filter(Impact.id.in_(ids)).all()

    @staticmethod
    def link_impacts(report_id: int, impact_ids: list[int]):
        for impact_id in impact_ids:
            db.session.add(
                ReportImpact(
                    report_id=report_id,
                    impact_id=impact_id
                )
            )
        db.session.flush()

    @staticmethod
    def create(name: str):
        normalized_name = (name or "").strip()
        if not normalized_name:
            return False, "El nombre del impacto es obligatorio", None
        existing_impact = Impact.query.filter(
            func.lower(Impact.name) == normalized_name.lower()
        ).first()
        if existing_impact:
            return False, "Ya existe un impacto con ese nombre", None
        impact = Impact(name=normalized_name)
        db.session.add(impact)
        db.session.flush()
        return True, "Impacto creado correctamente", impact
    
    @staticmethod
    def delete(impact_id: int):
        impact = Impact.query.get(impact_id)
        if not impact:
            return False, "Impacto no encontrado"
        if (impact.name or "").strip().lower() == "otro":
            return False, "El impacto 'Otro' es un registro obligatorio y no puede eliminarse"
        relation = ReportImpact.query.filter_by(impact_id=impact_id).first()
        if relation:
            return False, "No se puede eliminar el impacto porque está asociado a uno o más reportes"
        db.session.delete(impact)
        db.session.flush()
        return True, "Impacto eliminado correctamente"