from flask import Flask
import app.domain.models
from flask_migrate import Migrate
from app.controllers.adminController import admin_bp
from app.controllers.reportController import report_bp
from app.extensions import db, login_manager, csrf, mail
from app.config import config_by_name, load_environment_file
from app.domain.models import (User, Behavior, Evidence, Impact, Report, ReportBehavior, ReportImpact)

migrate = Migrate()

def create_app(config_name="development"):
    load_environment_file(config_name)

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    app.register_blueprint(report_bp)
    app.register_blueprint(admin_bp)

    config_class = config_by_name[config_name]
    if hasattr(config_class, "init_app"):
        config_class.init_app(app)

    return app