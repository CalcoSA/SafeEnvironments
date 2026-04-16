import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy.engine import URL

BASE_DIR = Path(__file__).resolve().parent.parent

def to_bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "on"}

def load_environment_file(env_name: str):
    env_files = {
        "development": BASE_DIR / ".env.development",
        "qa": BASE_DIR / ".env.qa",
        "production": BASE_DIR / ".env.production",
    }

    env_file = env_files.get(env_name, BASE_DIR / ".env.development")

    if env_file.exists():
        load_dotenv(env_file, override=True)

def build_database_uri():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    return URL.create(
        drivername=os.getenv("DB_DRIVER", "mysql+pymysql"),
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "formulario_acoso"),
        query={"charset": "utf8mb4"},
    ).render_as_string(hide_password=False)

class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        app.config["APP_NAME"] = os.getenv("APP_NAME", "Formulario de Reporte de Acoso Sexual")
        app.config["APP_ENV"] = os.getenv("APP_ENV", "development")

        app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
        app.config["WTF_CSRF_SECRET_KEY"] = os.getenv("WTF_CSRF_SECRET_KEY", app.config["SECRET_KEY"])

        app.config["WP_SHARED_SECRET"] = os.getenv("WP_SHARED_SECRET")
        app.config["INTRANET_URL"] = os.getenv("INTRANET_URL")
        app.config["ACCESS_MAX_AGE"] = int(os.getenv("ACCESS_MAX_AGE", "300"))

        app.config["ADMIN_INTRANET_USERS"] = {
            user.strip().lower()
            for user in os.getenv("ADMIN_INTRANET_USERS", "").split(",")
            if user.strip()
        }

        app.config["SQLALCHEMY_DATABASE_URI"] = build_database_uri()
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        app.config["MAIL_SERVER"] = os.getenv("MAIL_HOST")
        app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", "587"))
        app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
        app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
        app.config["MAIL_USE_TLS"] = to_bool(os.getenv("MAIL_USE_TLS"), True)
        app.config["MAIL_USE_SSL"] = to_bool(os.getenv("MAIL_USE_SSL"), False)
        app.config["MAIL_FROM_EMAIL"] = os.getenv("MAIL_FROM_EMAIL")
        app.config["MAIL_FROM_NAME"] = os.getenv("MAIL_FROM_NAME", "Canal Confidencial")
        app.config["MAIL_DEFAULT_SENDER"] = (
            os.getenv("MAIL_FROM_NAME", "Canal Confidencial"),
            os.getenv("MAIL_FROM_EMAIL")
        )
        app.config["CASE_NOTIFICATION_EMAILS"] = [
            email.strip()
            for email in os.getenv("CASE_NOTIFICATION_EMAILS", "").split(",")
            if email.strip()
        ]

        private_storage_path = Path(
            os.getenv("PRIVATE_STORAGE_PATH", str(BASE_DIR / "private_storage"))
        )
        evidence_upload_dir = Path(
            os.getenv("EVIDENCE_UPLOAD_DIR", str(private_storage_path / "evidencias"))
        )
        pdf_output_dir = Path(
            os.getenv("PDF_OUTPUT_DIR", str(BASE_DIR / "generated_pdfs"))
        )

        app.config["PRIVATE_STORAGE_PATH"] = private_storage_path
        app.config["EVIDENCE_UPLOAD_DIR"] = evidence_upload_dir
        app.config["PDF_OUTPUT_DIR"] = pdf_output_dir

        app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", 10 * 1024 * 1024))
        app.config["ALLOWED_FILE_EXTENSIONS"] = {
            ext.strip().lower()
            for ext in os.getenv(
                "ALLOWED_FILE_EXTENSIONS",
                "pdf,png,jpg,jpeg,doc,docx"
            ).split(",")
            if ext.strip()
        }

        app.config["SESSION_COOKIE_HTTPONLY"] = True
        app.config["SESSION_COOKIE_SECURE"] = to_bool(os.getenv("SESSION_COOKIE_SECURE"), False)
        app.config["SESSION_COOKIE_SAMESITE"] = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
        app.config["REMEMBER_COOKIE_HTTPONLY"] = True
        app.config["REMEMBER_COOKIE_SECURE"] = to_bool(os.getenv("REMEMBER_COOKIE_SECURE"), False)
        app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
            minutes=int(os.getenv("SESSION_LIFETIME_MINUTES", "30"))
        )

        app.config["WTF_CSRF_ENABLED"] = True
        app.config["WTF_CSRF_TIME_LIMIT"] = int(os.getenv("WTF_CSRF_TIME_LIMIT", "3600"))
        app.config["LOG_LEVEL"] = os.getenv("LOG_LEVEL", "INFO")
        app.config["AUDIT_LOG_ENABLED"] = to_bool(os.getenv("AUDIT_LOG_ENABLED"), True)

        private_storage_path.mkdir(parents=True, exist_ok=True)
        evidence_upload_dir.mkdir(parents=True, exist_ok=True)
        pdf_output_dir.mkdir(parents=True, exist_ok=True)

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False

class QaConfig(BaseConfig):
    DEBUG = False
    TESTING = True

class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False

config_by_name = {
    "development": DevelopmentConfig,
    "qa": QaConfig,
    "production": ProductionConfig,
}