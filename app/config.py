import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy.engine import URL

BASE_DIR = Path(__file__).resolve().parent.parent
#load_dotenv(BASE_DIR / ".env.development")

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
    APP_NAME = os.getenv("APP_NAME", "Formulario de Reporte de Acoso Sexual")
    APP_ENV = os.getenv("APP_ENV", "development")

    SECRET_KEY = os.getenv("SECRET_KEY")
    WTF_CSRF_SECRET_KEY = os.getenv("WTF_CSRF_SECRET_KEY", SECRET_KEY)

    WP_SHARED_SECRET = os.getenv("WP_SHARED_SECRET")
    INTRANET_URL = os.getenv("INTRANET_URL")
    ACCESS_MAX_AGE = int(os.getenv("ACCESS_MAX_AGE", "300"))

    ADMIN_INTRANET_USERS = {
        user.strip().lower()
        for user in os.getenv("ADMIN_INTRANET_USERS", "").split(",")
        if user.strip()
    }

    SQLALCHEMY_DATABASE_URI = build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv("MAIL_HOST")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_USE_TLS = to_bool(os.getenv("MAIL_USE_TLS"), True)
    MAIL_USE_SSL = to_bool(os.getenv("MAIL_USE_SSL"), False)
    MAIL_FROM_EMAIL = os.getenv("MAIL_FROM_EMAIL")
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Canal Confidencial")
    MAIL_DEFAULT_SENDER = (
        os.getenv("MAIL_FROM_NAME", "Canal Confidencial"),
        os.getenv("MAIL_FROM_EMAIL")
    )
    CASE_NOTIFICATION_EMAILS = [
        email.strip()
        for email in os.getenv("CASE_NOTIFICATION_EMAILS", "").split(",")
        if email.strip()
    ]

    PRIVATE_STORAGE_PATH = Path(
        os.getenv("PRIVATE_STORAGE_PATH", str(BASE_DIR / "private_storage"))
    )
    EVIDENCE_UPLOAD_DIR = Path(
        os.getenv("EVIDENCE_UPLOAD_DIR", str(PRIVATE_STORAGE_PATH / "evidencias"))
    )
    PDF_OUTPUT_DIR = Path(
        os.getenv("PDF_OUTPUT_DIR", str(BASE_DIR / "generated_pdfs"))
    )

    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 10 * 1024 * 1024))  # 10 MB
    ALLOWED_FILE_EXTENSIONS = {
        ext.strip().lower()
        for ext in os.getenv(
            "ALLOWED_FILE_EXTENSIONS",
            "pdf,png,jpg,jpeg,doc,docx"
        ).split(",")
        if ext.strip()
    }

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = to_bool(os.getenv("SESSION_COOKIE_SECURE"), False)
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = to_bool(os.getenv("REMEMBER_COOKIE_SECURE"), False)
    PERMANENT_SESSION_LIFETIME = timedelta(
        minutes=int(os.getenv("SESSION_LIFETIME_MINUTES", "30"))
    )

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = int(os.getenv("WTF_CSRF_TIME_LIMIT", "3600"))

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    AUDIT_LOG_ENABLED = to_bool(os.getenv("AUDIT_LOG_ENABLED"), True)

    @staticmethod
    def init_app(app):
        BaseConfig.PRIVATE_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
        BaseConfig.EVIDENCE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        BaseConfig.PDF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False

class QaConfig(BaseConfig):
    DEBUG = False
    TESTING = True

class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Lax"

config_by_name = {
    "development": DevelopmentConfig,
    "qa": QaConfig,
    "production": ProductionConfig,
}