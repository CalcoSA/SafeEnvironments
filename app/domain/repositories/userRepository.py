from app.extensions import db
from app.domain.models.user import User

class UserRepository:
    @staticmethod
    def get_by_document(document: str):
        return User.query.filter_by(document=document).first()

    @staticmethod
    def get_by_email(email: str):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def create(data: dict):
        user = User(**data)
        db.session.add(user)
        db.session.flush()
        return user

    @staticmethod
    def update(user: User, data: dict):
        for key, value in data.items():
            setattr(user, key, value)
        db.session.flush()
        return user

    @staticmethod
    def create_or_update_by_document(data: dict):
        normalized_document = (data.get("document") or "").strip()
        if not normalized_document:
            return False, "El número de documento es obligatorio", None
        normalized_email = (data.get("email") or "").strip().lower()
        if normalized_email:
            email_owner = User.query.filter(
                db.func.lower(User.email) == normalized_email
            ).first()
            if email_owner and email_owner.document != normalized_document:
                return False, "El correo electrónico ya está asociado a otro usuario", None
        cleaned_data = {
            "name": (data.get("name") or "").strip(),
            "document": normalized_document,
            "email": normalized_email or None,
            "phone": (data.get("phone") or "").strip() or None,
            "role": data.get("role") or "reporter",
            "area": (data.get("area") or "").strip() or None,
            "position": (data.get("position") or "").strip() or None,
        }
        existing_user = User.query.filter_by(document=normalized_document).first()
        if existing_user:
            for key, value in cleaned_data.items():
                setattr(existing_user, key, value)
            db.session.flush()
            return True, "Usuario actualizado correctamente", existing_user
        new_user = User(**cleaned_data)
        db.session.add(new_user)
        db.session.flush()
        return True, "Usuario creado correctamente", new_user