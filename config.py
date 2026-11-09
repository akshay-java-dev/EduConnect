import os
from pathlib import Path
ROOT = Path(__file__).resolve().parent
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-this-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{ROOT / 'instance' / 'educonnect.db'}").replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(ROOT / "instance" / "uploads"))
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024
