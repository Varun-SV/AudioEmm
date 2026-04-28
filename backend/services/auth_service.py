from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db.models import OAuthAccount, User

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return _pwd.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd.verify(plain, hashed)


# ── JWT helpers ───────────────────────────────────────────────────────────────

def _make_token(data: dict, expires_delta: timedelta) -> str:
    payload = {**data, "exp": datetime.now(timezone.utc) + expires_delta}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: str) -> str:
    return _make_token(
        {"sub": user_id, "type": "access"},
        timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(user_id: str) -> str:
    return _make_token(
        {"sub": user_id, "type": "refresh"},
        timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str, expected_type: str = "access") -> str:
    """Decode a JWT and return the user_id (sub), raising ValueError on failure."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("type") != expected_type:
            raise ValueError("Wrong token type")
        user_id: str = payload["sub"]
        return user_id
    except JWTError as exc:
        raise ValueError(str(exc)) from exc


# ── DB helpers ────────────────────────────────────────────────────────────────

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    return await db.get(User, user_id)


async def create_user(
    db: AsyncSession,
    email: str,
    password: str | None,
    display_name: str | None = None,
) -> User:
    user = User(
        email=email,
        hashed_password=hash_password(password) if password else None,
        display_name=display_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_or_create_oauth_user(
    db: AsyncSession,
    provider: str,
    provider_user_id: str,
    email: str,
    display_name: str | None = None,
) -> User:
    """Return an existing user linked to this OAuth identity, or create one."""
    result = await db.execute(
        select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_user_id == provider_user_id,
        )
    )
    oauth = result.scalar_one_or_none()
    if oauth:
        return await db.get(User, oauth.user_id)

    # Check if a user with this email exists (link OAuth to it)
    user = await get_user_by_email(db, email)
    if not user:
        user = await create_user(db, email=email, password=None, display_name=display_name)
        user.is_verified = True

    oauth_link = OAuthAccount(
        user_id=user.id,
        provider=provider,
        provider_user_id=str(provider_user_id),
    )
    db.add(oauth_link)
    await db.commit()
    return user
