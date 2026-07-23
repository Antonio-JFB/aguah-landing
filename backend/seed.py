from __future__ import annotations

import argparse
import getpass

from .auth import hash_password
from .db import init_db, upsert_user


def main() -> None:
    parser = argparse.ArgumentParser(description="Alta o actualizacion de usuarios de la landing")
    parser.add_argument("--username", required=True)
    parser.add_argument("--cliente", required=True, help="ej. aguah")
    parser.add_argument("--role", default="client")
    parser.add_argument("--full-name", default=None)
    parser.add_argument("--email", default=None, help="Opcional, solo para contacto")
    parser.add_argument("--password", default=None, help="Si se omite, se pide de forma interactiva")
    args = parser.parse_args()

    password = args.password or getpass.getpass("Contrasena: ")
    init_db()
    upsert_user(
        username=args.username,
        password_hash=hash_password(password),
        cliente=args.cliente,
        role=args.role,
        full_name=args.full_name,
        email=args.email,
    )
    print(f"Usuario {args.username} creado/actualizado para cliente '{args.cliente}'.")


if __name__ == "__main__":
    main()
