from app.domain.repositories.behaviorRepository import BehaviorRepository
from app.domain.repositories.impactRepository import ImpactRepository
from app.extensions import db

class CatalogService:
    @staticmethod
    def get_behaviors():
        return BehaviorRepository.get_all()

    @staticmethod
    def get_impacts():
        return ImpactRepository.get_all()

    @staticmethod
    def create_behavior(name: str):
        try:
            success, message, behavior = BehaviorRepository.create(name)
            if not success:
                db.session.rollback()
                return success, message, behavior
            db.session.commit()
            return success, message, behavior
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def delete_behavior(behavior_id: int):
        try:
            success, message = BehaviorRepository.delete(behavior_id)
            if not success:
                db.session.rollback()
                return success, message
            db.session.commit()
            return success, message
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def create_impact(name: str):
        try:
            success, message, impact = ImpactRepository.create(name)
            if not success:
                db.session.rollback()
                return success, message, impact
            db.session.commit()
            return success, message, impact
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def delete_impact(impact_id: int):
        try:
            success, message = ImpactRepository.delete(impact_id)
            if not success:
                db.session.rollback()
                return success, message
            db.session.commit()
            return success, message
        except Exception:
            db.session.rollback()
            raise