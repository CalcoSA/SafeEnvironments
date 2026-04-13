from app.extensions import db

class ReportBehavior(db.Model):
    __tablename__ = "report_behaviors"

    report_id = db.Column(db.Integer, db.ForeignKey("reports.id"), primary_key=True)
    behavior_id = db.Column(db.Integer, db.ForeignKey("behaviors.id"), primary_key=True)

    behavior = db.relationship("Behavior")   
    