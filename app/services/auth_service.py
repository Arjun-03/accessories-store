from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AdminSession, AdminUser
from app.security import verify_password
from app.utils import generate_session_token

SESSION_DURATION = timedelta(days=7)


def authenticate(db: Session, email: str, password: str) -> AdminUser | None:
    admin = db.execute(
        select(AdminUser).where(AdminUser.email == email, AdminUser.is_active.is_(True))
    ).scalar_one_or_none()

    if admin is None:
        return None
    if not verify_password(password, admin.password_hash):
        return None
    return admin


def create_session(db: Session, admin: AdminUser) -> AdminSession:
    session = AdminSession(
        session_token=generate_session_token(),
        admin_user_id=admin.id,
        expires_at=datetime.now(UTC) + SESSION_DURATION,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_valid_session(db: Session, token: str | None) -> AdminSession | None:
    if not token:
        return None
    session = db.execute(
        select(AdminSession).where(AdminSession.session_token == token)
    ).scalar_one_or_none()
    if session is None:
        return None
    if session.expires_at < datetime.now(UTC):
        db.delete(session)
        db.commit()
        return None
    return session


def delete_session(db: Session, token: str) -> None:
    session = db.execute(
        select(AdminSession).where(AdminSession.session_token == token)
    ).scalar_one_or_none()
    if session is not None:
        db.delete(session)
        db.commit()
