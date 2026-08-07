import getpass
import sys

from app.db import SessionLocal
from app.models import AdminUser
from app.security import hash_password


def create_admin():
    email = input("Admin email: ").strip()
    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm password: ")

    if password != confirm:
        print("Passwords do not match.")
        sys.exit(1)

    if len(password) < 8:
        print("Password must be at least 8 characters.")
        sys.exit(1)

    db = SessionLocal()
    try:
        existing = db.query(AdminUser).filter_by(email=email).first()
        if existing is not None:
            print(f"An admin with email {email} already exists.")
            sys.exit(1)

        admin = AdminUser(email=email, password_hash=hash_password(password))
        db.add(admin)
        db.commit()
        print(f"Admin created: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
