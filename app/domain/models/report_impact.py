from app.extensions import db

class ReportImpact(db.Model):
    __tablename__ = "report_impacts"

    report_id = db.Column(db.Integer, db.ForeignKey("reports.id"), primary_key=True)
    impact_id = db.Column(db.Integer, db.ForeignKey("impacts.id"), primary_key=True)

    impact = db.relationship("Impact")