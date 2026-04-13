from app.extensions import db

class Behavior(db.Model):
    __tablename__ = "behaviors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)