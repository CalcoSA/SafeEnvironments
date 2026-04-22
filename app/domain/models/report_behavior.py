from app.extensions import db

class ReportBehavior(db.Model):
    __tablename__ = "report_behaviors"

    report_id = db.Column(db.BigInteger, db.ForeignKey("reports.id"), nullable=False)
    behavior_id = db.Column(db.Integer, db.ForeignKey("behaviors.id"), primary_key=True)

    behavior = db.relationship("Behavior")