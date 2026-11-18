"""
Application configuration.

All settings can be overridden with a .env file (see .env.example).
"""
import os

from dotenv import load_dotenv

# Load variables from backend/.env if the file exists.
load_dotenv()


class Config:
    """Simple configuration object used by the Flask app."""

    # MongoDB connection string and database name
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017")
    DB_NAME = os.getenv("DB_NAME", "iafs")

    # Secret used to sign login tokens. CHANGE THIS before sharing the project.
    JWT_SECRET = os.getenv("JWT_SECRET", "iafs-dev-secret-change-me-in-production")
    JWT_EXPIRES_HOURS = int(os.getenv("JWT_EXPIRES_HOURS", "12"))

    # Allowed frontend origins (comma separated or * for wildcard)
    _cors_env = os.getenv("CORS_ORIGINS", "*").strip()
    if _cors_env == "*" or not _cors_env:
        CORS_ORIGINS = "*"
    else:
        CORS_ORIGINS = [o.strip() for o in _cors_env.split(",") if o.strip()]

    # Demo teacher account is created by seed.py using this invite code.
    # Students cannot self-register as teachers.
    TEACHER_INVITE_CODE = os.getenv("TEACHER_INVITE_CODE", "IAFS2026")

    # Automatically seed fresh cloud database if empty on startup
    AUTO_SEED = os.getenv("AUTO_SEED", "true").lower() in ("true", "1", "yes")
