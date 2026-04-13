from app.extensions import db
from datetime import datetime
from app.domain.models.report import Report

class ReportRepository:
    @staticmethod
    def get_all(status=None, page=1, per_page=10):
        query = Report.query.order_by(Report.created_at.desc())

        if status:
            query = query.filter(Report.status == status)

        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def get_by_id(report_id: int):
        return Report.query.get(report_id)

    @staticmethod
    def create(data: dict):
        report = Report(**data)
        db.session.add(report)
        db.session.flush()
        return report

    @staticmethod
    def update(report: Report, data: dict):
        for key, value in data.items():
            setattr(report, key, value)
        db.session.flush()
        return report