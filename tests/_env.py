import os
import tempfile

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("JWT_SECRET", "test-secret-for-ci-only")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("COOKIE_SECURE", "false")
os.environ.setdefault("COOKIE_DOMAIN", "")  # cookie host-only: TestClient no usa argentumdevelopment.com
os.environ.setdefault("DB_PATH", os.path.join(tempfile.gettempdir(), "aguah_landing_test.db"))
