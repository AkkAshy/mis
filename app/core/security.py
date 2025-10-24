from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from pydantic import SecretStr
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: Any, hashed_password: str) -> bool:
    print(f"Type: {type(plain_password)}, Value: {repr(plain_password)}")
    password = _to_str_password(plain_password)
    if len(password) > 72:
        password = password[:72]
    return pwd_context.verify(password, hashed_password)

def _to_str_password(password: Any) -> str:
    """Normalize incoming password values to a plain str.

    Handles pydantic.SecretStr and other non-str inputs. Always returns
    a UTF-8 string whose encoded length will be <= 72 bytes after
    truncation applied in get_password_hash.
    """
    if isinstance(password, SecretStr):
        return password.get_secret_value()
    if password is None:
        return ""
    return str(password)

def get_password_hash(password: Any) -> str:
    """Hash password for storage.

    Bcrypt (used by passlib) supports a maximum of 72 bytes. Here we
    normalize the password to str, then truncate to 72 characters
    before hashing. This avoids the ValueError raised by bcrypt when
    given longer secrets.
    """
    pw = _to_str_password(password)
    # Truncate password to 72 characters for bcrypt compatibility
    if len(pw) > 72:
        pw = pw[:72]
    return pwd_context.hash(pw)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None