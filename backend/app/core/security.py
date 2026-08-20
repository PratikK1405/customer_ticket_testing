from jose import jwt, JWTError
from backend.app.config import settings

ALGORITHM = "HS256"

def decode_supabase_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SUPABASE_JWT_SECRET, algorithms=[ALGORITHM], audience="authenticated")
    except JWTError as e:
        raise ValueError(str(e))