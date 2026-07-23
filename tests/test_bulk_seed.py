import tests._env  # noqa: F401  (debe importarse antes que backend.config)

import csv
import tempfile
import unittest
from pathlib import Path

from backend.auth import verify_password
from backend.bulk_seed import main
from backend.db import get_user_by_username


class BulkSeedTests(unittest.TestCase):
    def test_imports_users_from_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "usuarios.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                writer.writerow(["user", "password", "name", "role"])
                writer.writerow(["prueba.bulk", "clave-temporal", "Prueba Bulk", "analista"])

            import sys

            old_argv = sys.argv
            sys.argv = ["bulk_seed.py", str(csv_path), "--cliente", "aguah"]
            try:
                main()
            finally:
                sys.argv = old_argv

            user = get_user_by_username("prueba.bulk")
            self.assertIsNotNone(user)
            self.assertEqual(user["cliente"], "aguah")
            self.assertEqual(user["role"], "analista")
            self.assertEqual(user["full_name"], "Prueba Bulk")
            self.assertTrue(verify_password("clave-temporal", user["password_hash"]))


if __name__ == "__main__":
    unittest.main()
