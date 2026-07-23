import tests._env  # noqa: F401  (debe importarse antes que backend.config)

import unittest

from backend.auth import AuthError, create_session_token, decode_session_token, hash_password, verify_password


class PasswordHashingTests(unittest.TestCase):
    def test_hash_and_verify_roundtrip(self):
        password_hash = hash_password("hunter2")
        self.assertTrue(verify_password("hunter2", password_hash))

    def test_verify_rejects_wrong_password(self):
        password_hash = hash_password("hunter2")
        self.assertFalse(verify_password("wrong", password_hash))


class SessionTokenTests(unittest.TestCase):
    def test_encode_decode_roundtrip(self):
        token = create_session_token(1, "usuario.prueba", "aguah", "client")
        payload = decode_session_token(token)
        self.assertEqual(payload["username"], "usuario.prueba")
        self.assertEqual(payload["cliente"], "aguah")

    def test_decode_rejects_garbage_token(self):
        with self.assertRaises(AuthError):
            decode_session_token("not-a-real-token")


if __name__ == "__main__":
    unittest.main()
