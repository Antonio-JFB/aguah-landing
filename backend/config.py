from pathlib import Path
import os

ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "frontend"

APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "8008"))

JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "10"))

COOKIE_NAME = os.getenv("COOKIE_NAME", "aguah_session")
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", ".argentumdevelopment.com") or None
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").lower() != "false"

DB_PATH = Path(os.getenv("DB_PATH", ROOT_DIR / "data" / "landing.db")).resolve()

ALLOWED_REDIRECT_SUFFIX = os.getenv("ALLOWED_REDIRECT_SUFFIX", ".argentumdevelopment.com")


def require_jwt_secret() -> None:
    if not JWT_SECRET and os.getenv("APP_ENV") != "test":
        raise RuntimeError(
            "JWT_SECRET no esta configurado. Define JWT_SECRET en el entorno antes de arrancar."
        )
