import logging
from flask import Flask
import app.domain.models
from flask_migrate import Migrate
from app.controllers.adminController import admin_bp
from app.controllers.reportController import report_bp
from app.extensions import db, login_manager, csrf, mail
from app.config import config_by_name, load_environment_file
from sqlalchemy.exc import ProgrammingError, OperationalError
from app.services.systemParameterService import SystemParameterService
from app.domain.models import (User, Behavior, Evidence, Impact, Report, ReportBehavior, ReportImpact, SystemParameter, report_History)

migrate = Migrate()

def create_app(config_name="development"):
    load_environment_file(config_name)

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    config_class = config_by_name[config_name]
    if hasattr(config_class, "init_app"):
        config_class.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    app.register_blueprint(report_bp)
    app.register_blueprint(admin_bp)

    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

    app.logger.info("Aplicación iniciada correctamente")
    app.logger.info("Entorno cargado: %s", config_name)
    app.logger.info("MAIL_SERVER=%s", app.config.get("MAIL_SERVER"))
    app.logger.info("MAIL_PORT=%s", app.config.get("MAIL_PORT"))
    app.logger.info("MAIL_USERNAME=%s", app.config.get("MAIL_USERNAME"))
    app.logger.info("MAIL_USE_TLS=%s", app.config.get("MAIL_USE_TLS"))
    app.logger.info("MAIL_DEFAULT_SENDER=%s", app.config.get("MAIL_DEFAULT_SENDER"))

    with app.app_context():
        try:
            SystemParameterService.ensure_default_parameters()
            app.logger.info("Parámetros del sistema verificados correctamente")
        except (ProgrammingError, OperationalError) as e:
            app.logger.warning("No se pudieron verificar los parámetros por un problema de base de datos: %s", str(e))

    return app