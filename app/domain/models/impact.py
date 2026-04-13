from app.extensions import db

class Impact(db.Model):
    __tablename__ = "impacts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)