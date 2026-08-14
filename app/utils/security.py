from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from app.configs import config
import random  # Generate auto number
from jose.exceptions import ExpiredSignatureError
from jose import jwt, JWTError
from app.exceptions.token_exception import ExpiredTokenError, InvalidTokenError
import secrets
import hashlib

RESET_LINK_EXPIRE_MINUTES = 5

# encryption and verify password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- HELPER: Hash ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password[:72])


# --- HELPER: Verify ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password[:72], hashed_password)


# --- HELPER: Create Token ---
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
    to_encode.update({"type": "access", "exp": expire})

    # Encode JWT
    return jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)


# --- HELPER: Create reset Token ---
def create_reset_token(user_id: str) -> str:
    """Create JWT contain user_id"""

    expire = datetime.now(timezone.utc) + timedelta(minutes=RESET_LINK_EXPIRE_MINUTES)
    payload = {"id": user_id, "type": "reset", "exp": expire}
    return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)


# --- HELPER: Verify Reset Token ---
def verify_reset_token(reset_token: str) -> str:
    """
    Verify reset JWT, return user_id.
    Raise exception if token wrong or expired.
    """
    try:
        payload = jwt.decode(
            reset_token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM]
        )
        if payload.get("type") != "reset":
            raise InvalidTokenError()

        return payload["id"]
    except ExpiredSignatureError:
        raise ExpiredTokenError("Reset token has expired. Please request a new one.")
    except JWTError:
        raise InvalidTokenError()


# --- HELPER: Generate OTP ---
def generate_otp() -> str:
    """Generate 6 numbers OTP - integer numbers (Mobile only)"""
    return f"{random.randint(0, 999999):06d}"


# --- HELPER: Generate Refresh Token ---
def create_refresh_token() -> tuple[str, str]:
    """Generate refresh token"""
    raw = secrets.token_urlsafe(config.REFRESH_TOKEN_LENGTH)

    # Raw for client, hash_token for database
    return raw, hash_token(raw)


# --- HELPER: Hash Refresh Token ---
def hash_token(token: str) -> str:
    """Hash Token by SHA-256 (hex with 64 characters)"""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
