"""Application configuration loaded from environment variables with safe local defaults."""
import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "gov-dss-dev-secret-key-change-in-production")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'database', 'gov_dss.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    ALLOWED_DOCUMENT_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "txt", "csv"}
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25 MB

    AI_MODEL_DIR = os.path.join(BASE_DIR, "ai_engine", "saved_models")
    AI_DATASET_PATH = os.path.join(BASE_DIR, "data", "dataset.csv")

    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    MINISTRIES = [
        "Ministry of Health",
        "Ministry of Education",
        "Ministry of Interior",
        "Ministry of Finance",
        "Ministry of Transportation",
        "Ministry of Energy",
        "Ministry of Agriculture",
        "Ministry of Justice",
        "Ministry of Housing",
        "Ministry of Labor",
    ]

    REPORT_CATEGORIES = [
        "Infrastructure",
        "Public Health",
        "Education",
        "Security",
        "Economy",
        "Environment",
        "Corruption & Compliance",
        "Public Services",
    ]

    PRIORITY_LEVELS = ["Low", "Medium", "High", "Critical"]


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
