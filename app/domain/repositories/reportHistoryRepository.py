from app.extensions import db
from app.domain.models.report_History import ReportHistory

class ReportHistoryRepository:
    @staticmethod
    def create(data: dict):
        item = ReportHistory(**data)
        db.session.add(item)
        db.session.flush()
        return item

    @staticmethod
    def get_by_report_id(report_id: int):
        return ReportHistory.query.filter_by(report_id=report_id).order_by(ReportHistory.created_at.asc()).all()