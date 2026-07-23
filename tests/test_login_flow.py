import tests._env  # noqa: F401  (debe importarse antes que backend.config)

import unittest

from fastapi.testclient import TestClient

from backend.auth import hash_password
from backend.config import COOKIE_NAME
from backend.db import init_db, upsert_user
from backend.main import app


class LoginFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        upsert_user(
            username="operador.aguah",
            password_hash=hash_password("clave-segura"),
            cliente="aguah",
            role="client",
        )
        cls.context = TestClient(app)
        cls.client = cls.context.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.context.__exit__(None, None, None)

    def setUp(self):
        self.client.cookies.clear()

    def test_health(self):
        self.assertEqual(self.client.get("/api/health").json(), {"status": "ok"})

    def test_root_redirects_to_login_when_anonymous(self):
        response = self.client.get("/", follow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "/login")

    def test_login_page_renders(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Argentum", response.text)

    def test_wrong_password_returns_401_without_cookie(self):
        response = self.client.post(
            "/login", data={"username": "operador.aguah", "password": "wrong"}
        )
        self.assertEqual(response.status_code, 401)
        self.assertNotIn(COOKIE_NAME, response.cookies)

    def test_correct_login_sets_cookie_and_redirects(self):
        response = self.client.post(
            "/login",
            data={"username": "operador.aguah", "password": "clave-segura"},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "/dashboards")
        self.assertIn(COOKIE_NAME, response.cookies)

    def test_dashboards_requires_session(self):
        response = self.client.get("/dashboards", follow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertTrue(response.headers["location"].startswith("/login"))

    def test_dashboards_lists_assigned_dashboard(self):
        self.client.post(
            "/login", data={"username": "operador.aguah", "password": "clave-segura"}
        )
        response = self.client.get("/dashboards")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Fugas y priorizaci", response.text)

    def test_open_redirect_is_rejected(self):
        response = self.client.post(
            "/login",
            data={
                "username": "operador.aguah",
                "password": "clave-segura",
                "next": "https://evil.example.com/phish",
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "/dashboards")

    def test_relative_next_is_honored(self):
        response = self.client.post(
            "/login",
            data={
                "username": "operador.aguah",
                "password": "clave-segura",
                "next": "/dashboards?foo=bar",
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "/dashboards?foo=bar")


if __name__ == "__main__":
    unittest.main()
