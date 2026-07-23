from __future__ import annotations

import html as html_lib
from contextlib import asynccontextmanager
from urllib.parse import urlparse

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from .auth import AuthError, create_session_token, decode_session_token, verify_password
from .config import (
    ALLOWED_REDIRECT_SUFFIX,
    COOKIE_DOMAIN,
    COOKIE_NAME,
    COOKIE_SECURE,
    FRONTEND_DIR,
    JWT_EXPIRE_HOURS,
    require_jwt_secret,
)
from .db import get_user_by_username, init_db
from .registry import dashboards_for


@asynccontextmanager
async def lifespan(app: FastAPI):
    require_jwt_secret()
    init_db()
    yield


app = FastAPI(
    title="Argentum - AguaH Landing",
    description="Login y acceso a los dashboards de Agua de Hermosillo.",
    version="1.0.0",
    lifespan=lifespan,
)


def _safe_next(next_url: str | None) -> str | None:
    if not next_url:
        return None
    parsed = urlparse(next_url)
    if parsed.netloc == "":
        return next_url
    if parsed.netloc.split(":")[0].endswith(ALLOWED_REDIRECT_SUFFIX):
        return next_url
    return None


def _current_session(request: Request) -> dict | None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    try:
        return decode_session_token(token)
    except AuthError:
        return None


def _render_login(next_url: str | None, error: bool = False) -> str:
    html = (FRONTEND_DIR / "login.html").read_text(encoding="utf-8")
    html = html.replace("{{next}}", html_lib.escape(_safe_next(next_url) or ""))
    error_html = '<div id="error" class="error">Usuario o contrasena invalidos.</div>' if error else ""
    return html.replace("{{error}}", error_html)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def root(request: Request):
    destination = "/dashboards" if _current_session(request) else "/login"
    return RedirectResponse(destination, status_code=303)


@app.get("/login", include_in_schema=False)
def login_page(next: str | None = None):
    return HTMLResponse(_render_login(next))


@app.post("/login", include_in_schema=False)
def login_submit(username: str = Form(...), password: str = Form(...), next: str = Form("")):
    user = get_user_by_username(username)
    if user is None or not verify_password(password, user["password_hash"]):
        return HTMLResponse(_render_login(next, error=True), status_code=401)

    token = create_session_token(user["id"], user["username"], user["cliente"], user["role"])
    destination = _safe_next(next) or "/dashboards"
    response = RedirectResponse(destination, status_code=303)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        domain=COOKIE_DOMAIN,
        path="/",
        max_age=JWT_EXPIRE_HOURS * 3600,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
    )
    return response


@app.get("/logout", include_in_schema=False)
def logout(next: str | None = None):
    response = RedirectResponse(_safe_next(next) or "/login", status_code=303)
    response.delete_cookie(COOKIE_NAME, domain=COOKIE_DOMAIN, path="/")
    return response


@app.get("/dashboards", include_in_schema=False)
def dashboards_page(request: Request):
    session = _current_session(request)
    if session is None:
        return RedirectResponse("/login?next=/dashboards", status_code=303)

    items = dashboards_for(session["cliente"])
    cards = "".join(
        f'<a class="card" href="{html_lib.escape(d["url"])}">'
        f'<h3>{html_lib.escape(d["name"])}</h3><p>{html_lib.escape(d["description"])}</p></a>'
        for d in items
    )
    html = (FRONTEND_DIR / "dashboards.html").read_text(encoding="utf-8")
    html = html.replace("{{username}}", html_lib.escape(session["username"]))
    html = html.replace("{{cards}}", cards or "<p>No hay dashboards asignados.</p>")
    return HTMLResponse(html)


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
