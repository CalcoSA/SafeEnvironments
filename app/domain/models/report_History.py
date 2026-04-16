from app.extensions import db
from datetime import datetime
import pytz

class ReportHistory(db.Model):
    __tablename__ = "report_history"

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey("reports.id"), nullable=False, index=True)
    status = db.Column(db.Enum("nuevo", "en_proceso", "finalizado", "archivado"), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    changed_by_user_login = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone("America/Bogota")).replace(tzinfo=None), nullable=False)
    report = db.relationship("Report", back_populates="history")