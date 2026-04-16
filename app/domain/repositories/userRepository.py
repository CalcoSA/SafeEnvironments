from app.extensions import db
from app.domain.models.user import User

class UserRepository:
    @staticmethod
    def get_all():
        return User.query.filter(User.role != "reporter").order_by(User.name.asc()).all()

    @staticmethod
    def get_by_id(user_id: int):
        return User.query.get(user_id)

    @staticmethod
    def get_by_document(document: str):
        return User.query.filter_by(document=document).first()

    @staticmethod
    def get_by_email(email: str):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_by_user_login(user_login: str):
        if not user_login:
            return None
        return User.query.filter(db.func.lower(User.user_login) == user_login.strip().lower()).first()

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
    def delete(user: User):
        db.session.delete(user)
        db.session.flush()

    @staticmethod
    def create_or_update_by_document(data: dict):
        normalized_document = (data.get("document") or "").strip()
        normalized_email = (data.get("email") or "").strip().lower()
        normalized_user_login = (data.get("user_login") or "").strip().lower() or None
        if not normalized_document:
            return False, "El número de documento es obligatorio", None
        if normalized_email:
            email_owner = User.query.filter(db.func.lower(User.email) == normalized_email).first()
            if email_owner and email_owner.document != normalized_document:
                return False, "El correo electrónico ya está asociado a otro usuario", None
        if normalized_user_login:
            login_owner = User.query.filter(db.func.lower(User.user_login) == normalized_user_login).first()
            if login_owner and login_owner.document != normalized_document:
                return False, "El usuario de intranet ya está asociado a otro usuario", None
        incoming_role = data.get("role") or "reporter"
        cleaned_data = {
            "name": (data.get("name") or "").strip(),
            "document": normalized_document,
            "email": normalized_email or None,
            "phone": (data.get("phone") or "").strip() or None,
            "area": (data.get("area") or "").strip() or None,
            "position": (data.get("position") or "").strip() or None,
        }
        existing_user = User.query.filter_by(document=normalized_document).first()
        if existing_user:
            for key, value in cleaned_data.items():
                setattr(existing_user, key, value)
            if normalized_user_login:
                existing_user.user_login = normalized_user_login
            if not existing_user.role or existing_user.role == "reporter":
                existing_user.role = incoming_role
            db.session.flush()
            return True, "Usuario actualizado correctamente", existing_user
        new_user = User(**cleaned_data, user_login=normalized_user_login, role=incoming_role)
        db.session.add(new_user)
        db.session.flush()
        return True, "Usuario creado correctamente", new_user