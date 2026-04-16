from app.extensions import db
from datetime import datetime

class SystemParameter(db.Model):
    __tablename__ = "system_parameters"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(255), nullable=True)