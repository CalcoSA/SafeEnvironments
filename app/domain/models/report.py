from app.extensions import db
from datetime import datetime
import pytz

class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    reporter_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    accused_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reporter_name = db.Column(db.String(150), nullable=False)
    reporter_area = db.Column(db.String(150), nullable=False)
    reporter_position = db.Column(db.String(150), nullable=False)
    accused_name = db.Column(db.String(150), nullable=False)
    accused_area = db.Column(db.String(150), nullable=False)
    accused_position = db.Column(db.String(150), nullable=False)
    narrative = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone("America/Bogota")).replace(tzinfo=None), nullable=False)
    closed_at = db.Column(db.DateTime, nullable=True)
    accused_relation = db.Column(
        db.Enum("jefe_directo", "companero", "persona_a_cargo", "proveedor", "cliente", "otro"),
        nullable=True
    )
    accused_relation_other = db.Column(db.String(150), nullable=True)
    frequency = db.Column(
        db.Enum("una_vez", "mas_de_una_vez", "reiterada"),
        nullable=True
    )
    has_evidence = db.Column(
        db.Enum("si", "no", "investigar_sin_pruebas"),
        nullable=False
    )
    current_risk = db.Column(
        db.Enum("si", "no", "no_segura"),
        nullable=True
    )
    psychological_support = db.Column(
        db.Enum("prioritario", "orientacion", "no", "mas_informacion"),
        nullable=True
    )
    status = db.Column(
        db.Enum("nuevo", "en_proceso", "finalizado", "archivado"),
        default="nuevo",
        nullable=False
    )
    reporter_user = db.relationship(
        "User",
        foreign_keys=[reporter_user_id],
        back_populates="reports_made"
    )
    accused_user = db.relationship(
        "User",
        foreign_keys=[accused_user_id],
        back_populates="reports_received"
    )
    behaviors = db.relationship(
        "ReportBehavior",
        cascade="all, delete-orphan"
    )
    impacts = db.relationship(
        "ReportImpact",
        cascade="all, delete-orphan"
    )
    evidences = db.relationship(
        "Evidence",
        cascade="all, delete-orphan"
    )
    history = db.relationship(
        "ReportHistory",
        back_populates="report",
        cascade="all, delete-orphan",
        order_by="ReportHistory.created_at.asc()"
    )