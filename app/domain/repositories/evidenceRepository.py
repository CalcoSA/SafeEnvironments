from app.extensions import db
from app.domain.models.evidence import Evidence

class EvidenceRepository:
    @staticmethod
    def create(data: dict):
        evidence = Evidence(**data)
        db.session.add(evidence)
        db.session.flush()
        return evidence

    @staticmethod
    def create_many(items: list[dict]):
        evidences = []
        for item in items:
            evidence = Evidence(**item)
            db.session.add(evidence)
            evidences.append(evidence)
        db.session.flush()
        return evidences

    @staticmethod
    def get_by_id(evidence_id: int):
        return Evidence.query.get(evidence_id)