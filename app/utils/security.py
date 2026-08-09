from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import jwt
from app.configs import config

# encryption and verify password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- HELPER: Hash, Verify, Create Token ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])


# --- HELPER: Verify ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password[:72], hashed_password)


# --- HELPER:  Create Token ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Helper: Create JWT Token
    - Copy payload data
    - Set expired time
    - Encode JWT
    - Return token string
    """
    to_encode = data.copy()

    # Token expire
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    # Encode JWT
    return jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
