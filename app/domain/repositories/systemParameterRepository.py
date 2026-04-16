from app.extensions import db
from app.domain.models.system_Parameter import SystemParameter

class SystemParameterRepository:
    @staticmethod
    def get_all():
        return SystemParameter.query.order_by(SystemParameter.key.asc()).all()

    @staticmethod
    def get_by_id(parameter_id: int):
        return SystemParameter.query.get(parameter_id)

    @staticmethod
    def get_by_key(key: str):
        if not key:
            return None
        return SystemParameter.query.filter_by(key=key.strip()).first()

    @staticmethod
    def create(data: dict):
        parameter = SystemParameter(**data)
        db.session.add(parameter)
        db.session.flush()
        return parameter

    @staticmethod
    def update(parameter: SystemParameter, data: dict):
        for key, value in data.items():
            setattr(parameter, key, value)
        db.session.flush()
        return parameter

    @staticmethod
    def delete(parameter: SystemParameter):
        db.session.delete(parameter)
        db.session.flush()