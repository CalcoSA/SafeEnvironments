from app.extensions import db
from app.domain.repositories.userRepository import UserRepository

class UserService:
    ALLOWED_ROLES = {"reporter", "user", "admin"}

    @staticmethod
    def get_all_users():
        return UserRepository.get_all()

    @staticmethod
    def get_user(user_id: int):
        return UserRepository.get_by_id(user_id)

    @staticmethod
    def create_user(form_data: dict):
        try:
            name = (form_data.get("name") or "").strip()
            user_login = (form_data.get("user_login") or "").strip().lower() or None
            document = (form_data.get("document") or "").strip() or None
            email = (form_data.get("email") or "").strip().lower() or None
            phone = (form_data.get("phone") or "").strip() or None
            area = (form_data.get("area") or "").strip() or None
            position = (form_data.get("position") or "").strip() or None
            role = (form_data.get("role") or "reporter").strip()

            if not name:
                raise Exception("El nombre es obligatorio")

            if role not in UserService.ALLOWED_ROLES:
                raise Exception("El rol seleccionado no es válido")

            if user_login:
                existing_login = UserRepository.get_by_user_login(user_login)
                if existing_login:
                    raise Exception("El user_login ya existe en otro usuario")

            if email:
                existing_email = UserRepository.get_by_email(email)
                if existing_email:
                    raise Exception("El correo electrónico ya existe en otro usuario")

            user = UserRepository.create({
                "name": name,
                "user_login": user_login,
                "document": document,
                "email": email,
                "phone": phone,
                "role": role,
                "area": area,
                "position": position,
            })

            db.session.commit()
            return user

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def update_user(user_id: int, form_data: dict):
        try:
            user = UserRepository.get_by_id(user_id)
            if not user:
                raise Exception("Usuario no encontrado")

            name = (form_data.get("name") or "").strip()
            user_login = (form_data.get("user_login") or "").strip().lower() or None
            document = (form_data.get("document") or "").strip() or None
            email = (form_data.get("email") or "").strip().lower() or None
            phone = (form_data.get("phone") or "").strip() or None
            area = (form_data.get("area") or "").strip() or None
            position = (form_data.get("position") or "").strip() or None
            role = (form_data.get("role") or "reporter").strip()

            if not name:
                raise Exception("El nombre es obligatorio")

            if role not in UserService.ALLOWED_ROLES:
                raise Exception("El rol seleccionado no es válido")

            if user_login:
                existing_login = UserRepository.get_by_user_login(user_login)
                if existing_login and existing_login.id != user.id:
                    raise Exception("El user_login ya existe en otro usuario")

            if email:
                existing_email = UserRepository.get_by_email(email)
                if existing_email and existing_email.id != user.id:
                    raise Exception("El correo electrónico ya existe en otro usuario")

            updated_user = UserRepository.update(user, {
                "name": name,
                "user_login": user_login,
                "document": document,
                "email": email,
                "phone": phone,
                "role": role,
                "area": area,
                "position": position,
            })

            db.session.commit()
            return updated_user

        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def delete_user(user_id: int):
        try:
            user = UserRepository.get_by_id(user_id)
            if not user:
                raise Exception("Usuario no encontrado")

            UserRepository.delete(user)
            db.session.commit()

        except Exception:
            db.session.rollback()
            raise