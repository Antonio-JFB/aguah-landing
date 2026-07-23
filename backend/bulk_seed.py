from __future__ import annotations

import argparse
import csv

from .auth import hash_password
from .db import init_db, upsert_user


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Alta masiva de usuarios desde un CSV con columnas: user,password,name,role"
    )
    parser.add_argument("csv_path")
    parser.add_argument("--cliente", required=True, help="ej. aguah")
    args = parser.parse_args()

    init_db()
    count = 0
    with open(args.csv_path, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            username = row["user"].strip()
            upsert_user(
                username=username,
                password_hash=hash_password(row["password"]),
                cliente=args.cliente,
                role=(row.get("role") or "client").strip() or "client",
                full_name=(row.get("name") or "").strip() or None,
            )
            count += 1

    print(f"{count} usuarios creados/actualizados para cliente '{args.cliente}'.")


if __name__ == "__main__":
    main()
