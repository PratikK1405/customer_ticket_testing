from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.core.supabase_client import supabase
from backend.app.schemas.auth import SignUpRequest, LoginRequest, RefreshRequest, TokenResponse
from backend.app.schemas.user import UserRead
from backend.app.models.user import User
from backend.app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", status_code=201)
async def signup(payload: SignUpRequest, db: AsyncSession = Depends(get_db)):
    try:
        res = supabase.auth.sign_up({"email": payload.email, "password": payload.password})
    except Exception as e:
        raise HTTPException(400, str(e))
    if not res.user:
        raise HTTPException(400, "Signup failed")

    new_user = User(id=res.user.id, email=res.user.email, password_hash="MANAGED_BY_SUPABASE_AUTH")
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "Signup successful", "user_id": str(new_user.id)}

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    try:
        res = supabase.auth.sign_in_with_password({"email": payload.email, "password": payload.password})
    except Exception as e:
        raise HTTPException(401, str(e))
    session = res.session
    if not session:
        raise HTTPException(401, "Invalid credentials")
    return TokenResponse(
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        expires_in=session.expires_in,
        user={"id": str(res.user.id), "email": res.user.email},
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest):
    try:
        res = supabase.auth.refresh_session(payload.refresh_token)
    except Exception as e:
        raise HTTPException(401, str(e))
    session = res.session
    return TokenResponse(
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        expires_in=session.expires_in,
        user={"id": str(res.user.id), "email": res.user.email},
    )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    return {"message": "Logged out"}

@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)):
    return current_user