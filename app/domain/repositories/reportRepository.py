from app.extensions import db
from datetime import datetime
import pytz
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
        return db.session.get(Report, report_id)

    @staticmethod
    def _generate_next_report_id():
        bogota_tz = pytz.timezone("America/Bogota")
        now = datetime.now(bogota_tz)

        date_prefix = now.strftime("%Y%m%d")
        day_start = int(f"{date_prefix}000")
        day_end = int(f"{date_prefix}999")

        last_report = (
            Report.query
            .filter(Report.id >= day_start, Report.id <= day_end)
            .order_by(Report.id.desc())
            .with_for_update()
            .first()
        )

        if last_report:
            last_sequence = int(str(last_report.id)[-3:])
            next_sequence = last_sequence + 1
        else:
            next_sequence = 1

        if next_sequence > 999:
            raise Exception("Se alcanzó el máximo de 999 reportes para el día actual")

        return int(f"{date_prefix}{next_sequence:03d}")

    @staticmethod
    def create(data: dict):
        if not data.get("id"):
            data["id"] = ReportRepository._generate_next_report_id()

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