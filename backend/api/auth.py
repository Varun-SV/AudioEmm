from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db.base import get_db
from db.models import User
from schemas.auth import RefreshRequest, TokenResponse, UserLogin, UserRead, UserRegister
from services.auth_service import (
    create_access_token,
    create_refresh_token,
    create_user,
    decode_token,
    get_or_create_oauth_user,
    get_user_by_email,
    get_user_by_id,
    verify_password,
)

_limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["auth"])


# ── Dependency ────────────────────────────────────────────────────────────────

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Not authenticated")
    token = auth.removeprefix("Bearer ").strip()
    try:
        user_id = decode_token(token, "access")
    except ValueError:
        raise HTTPException(401, "Invalid or expired token")
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(401, "User not found")
    return user


async def get_optional_user(request: Request, db: AsyncSession = Depends(get_db)) -> User | None:
    """Returns the current user if authenticated, or None for anonymous requests."""
    try:
        return await get_current_user(request, db)
    except HTTPException:
        return None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=201)
@_limiter.limit("10/minute")
async def register(request: Request, body: UserRegister, db: AsyncSession = Depends(get_db)):
    if await get_user_by_email(db, body.email):
        raise HTTPException(409, "Email already registered")
    user = await create_user(db, body.email, body.password, body.display_name)
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/login", response_model=TokenResponse)
@_limiter.limit("10/minute")
async def login(request: Request, body: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, body.email)
    if not user or not user.hashed_password or not verify_password(body.password, user.hashed_password):
        raise HTTPException(401, "Invalid email or password")
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        user_id = decode_token(body.refresh_token, "refresh")
    except ValueError:
        raise HTTPException(401, "Invalid refresh token")
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(401, "User not found")
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)):
    return UserRead(
        id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name,
        is_verified=current_user.is_verified,
    )


# ── Google OAuth ──────────────────────────────────────────────────────────────

@router.get("/google/redirect")
async def google_redirect():
    if not settings.google_client_id:
        raise HTTPException(501, "Google OAuth not configured")
    from authlib.integrations.httpx_client import AsyncOAuth2Client
    redirect_uri = f"{settings.oauth_redirect_base}/api/auth/google/callback"
    async with AsyncOAuth2Client(client_id=settings.google_client_id) as client:
        uri, _ = client.create_authorization_url(
            "https://accounts.google.com/o/oauth2/v2/auth",
            redirect_uri=redirect_uri,
            scope="openid email profile",
        )
    return RedirectResponse(uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    if not settings.google_client_id:
        raise HTTPException(501, "Google OAuth not configured")
    from authlib.integrations.httpx_client import AsyncOAuth2Client
    redirect_uri = f"{settings.oauth_redirect_base}/api/auth/google/callback"
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(400, "Missing code parameter")

    async with AsyncOAuth2Client(
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
    ) as client:
        token = await client.fetch_token(
            "https://oauth2.googleapis.com/token",
            code=code,
            redirect_uri=redirect_uri,
        )
        userinfo = await client.get("https://www.googleapis.com/oauth2/v3/userinfo")
        userinfo = userinfo.json()

    user = await get_or_create_oauth_user(
        db,
        provider="google",
        provider_user_id=userinfo["sub"],
        email=userinfo["email"],
        display_name=userinfo.get("name"),
    )
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    # Redirect to frontend with tokens as query params (frontend reads and stores them)
    return RedirectResponse(
        f"{settings.oauth_redirect_base}/?access_token={access}&refresh_token={refresh}"
    )


# ── GitHub OAuth ──────────────────────────────────────────────────────────────

@router.get("/github/redirect")
async def github_redirect():
    if not settings.github_client_id:
        raise HTTPException(501, "GitHub OAuth not configured")
    from authlib.integrations.httpx_client import AsyncOAuth2Client
    redirect_uri = f"{settings.oauth_redirect_base}/api/auth/github/callback"
    async with AsyncOAuth2Client(client_id=settings.github_client_id) as client:
        uri, _ = client.create_authorization_url(
            "https://github.com/login/oauth/authorize",
            redirect_uri=redirect_uri,
            scope="user:email",
        )
    return RedirectResponse(uri)


@router.get("/github/callback")
async def github_callback(request: Request, db: AsyncSession = Depends(get_db)):
    if not settings.github_client_id:
        raise HTTPException(501, "GitHub OAuth not configured")
    from authlib.integrations.httpx_client import AsyncOAuth2Client
    redirect_uri = f"{settings.oauth_redirect_base}/api/auth/github/callback"
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(400, "Missing code parameter")

    async with AsyncOAuth2Client(
        client_id=settings.github_client_id,
        client_secret=settings.github_client_secret,
    ) as client:
        token = await client.fetch_token(
            "https://github.com/login/oauth/access_token",
            code=code,
            redirect_uri=redirect_uri,
        )
        user_resp = await client.get("https://api.github.com/user")
        gh_user = user_resp.json()

        # GitHub may not expose email in /user — fetch primary email separately
        email = gh_user.get("email")
        if not email:
            emails_resp = await client.get("https://api.github.com/user/emails")
            for e in emails_resp.json():
                if e.get("primary"):
                    email = e["email"]
                    break

    if not email:
        raise HTTPException(400, "Could not retrieve email from GitHub account")

    user = await get_or_create_oauth_user(
        db,
        provider="github",
        provider_user_id=str(gh_user["id"]),
        email=email,
        display_name=gh_user.get("name") or gh_user.get("login"),
    )
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    return RedirectResponse(
        f"{settings.oauth_redirect_base}/?access_token={access}&refresh_token={refresh}"
    )
