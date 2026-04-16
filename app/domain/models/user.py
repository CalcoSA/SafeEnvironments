from app.extensions import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    user_login = db.Column(db.String(100), unique=True, nullable=True, index=True)
    document = db.Column(db.String(50), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(30),  nullable=True)
    role = db.Column(db.Enum("reporter", "user", "admin", name="user_roles"), nullable=False, default="reporter")
    area = db.Column(db.String(150), nullable=True)
    position = db.Column(db.String(150), nullable=True)

    reports_made = db.relationship(
        "Report",
        foreign_keys="Report.reporter_user_id",
        back_populates="reporter_user"
    )
    reports_received = db.relationship(
        "Report",
        foreign_keys="Report.accused_user_id",
        back_populates="accused_user"
    )