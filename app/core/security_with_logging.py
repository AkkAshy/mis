from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from pydantic import SecretStr
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: Any, hashed_password: str) -> bool:
    """
    Проверка пароля с детальным логированием
    """
    try:
        logger.info("🔐 verify_password: Начало проверки пароля")
        logger.info(f"   Plain password type: {type(plain_password)}")
        logger.info(f"   Plain password repr: {repr(plain_password)}")
        logger.info(f"   Hashed password length: {len(hashed_password)}")
        logger.info(f"   Hashed password (first 30 chars): {hashed_password[:30]}...")
        
        # Нормализация пароля
        password = _to_str_password(plain_password)
        logger.info(f"   Normalized password type: {type(password)}")
        logger.info(f"   Normalized password length: {len(password)}")
        
        # Truncate если нужно
        if len(password) > 72:
            logger.warning(f"   ⚠️ Password truncated from {len(password)} to 72 chars")
            password = password[:72]
        
        # Проверка
        logger.info("   Calling pwd_context.verify()...")
        result = pwd_context.verify(password, hashed_password)
        logger.info(f"   Verification result: {result}")
        
        if result:
            logger.info("✅ verify_password: Пароль верный")
        else:
            logger.warning("⚠️ verify_password: Пароль неверный")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ verify_password: Ошибка при проверке пароля: {str(e)}")
        logger.error(f"   Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"   Traceback: {traceback.format_exc()}")
        raise


def _to_str_password(password: Any) -> str:
    """
    Нормализация пароля с логированием
    """
    logger.info("🔄 _to_str_password: Нормализация пароля")
    logger.info(f"   Input type: {type(password)}")
    
    if isinstance(password, SecretStr):
        logger.info("   Converting from SecretStr")
        result = password.get_secret_value()
    elif password is None:
        logger.warning("   ⚠️ Password is None, returning empty string")
        result = ""
    else:
        logger.info("   Converting to str")
        result = str(password)
    
    logger.info(f"   Result type: {type(result)}")
    logger.info(f"   Result length: {len(result)}")
    
    return result


def get_password_hash(password: Any) -> str:
    """
    Хеширование пароля с детальным логированием
    """
    try:
        logger.info("🔐 get_password_hash: Начало хеширования пароля")
        logger.info(f"   Input type: {type(password)}")
        logger.info(f"   Input repr: {repr(password)}")
        
        # Нормализация
        pw = _to_str_password(password)
        logger.info(f"   Normalized password length: {len(pw)}")
        
        # Truncate для совместимости
        if len(pw) > 72:
            logger.warning(f"   ⚠️ Truncating password from {len(pw)} to 72 chars")
            pw = pw[:72]
        
        # Хеширование
        logger.info("   Calling pwd_context.hash()...")
        hashed = pwd_context.hash(pw)
        logger.info(f"   Hash generated, length: {len(hashed)}")
        logger.info(f"   Hash (first 30 chars): {hashed[:30]}...")
        
        logger.info("✅ get_password_hash: Пароль успешно захеширован")
        return hashed
        
    except Exception as e:
        logger.error(f"❌ get_password_hash: Ошибка при хешировании: {str(e)}")
        logger.error(f"   Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"   Traceback: {traceback.format_exc()}")
        raise


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Создание JWT токена с логированием
    """
    try:
        logger.info("🔑 create_access_token: Создание токена")
        logger.info(f"   Data: {data}")
        
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
            logger.info(f"   Custom expiration delta: {expires_delta}")
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
            logger.info(f"   Default expiration: {settings.access_token_expire_minutes} minutes")
        
        to_encode.update({"exp": expire})
        logger.info(f"   Token will expire at: {expire}")
        
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        logger.info(f"   Token created, length: {len(encoded_jwt)}")
        logger.info(f"   Token (first 30 chars): {encoded_jwt[:30]}...")
        
        logger.info("✅ create_access_token: Токен успешно создан")
        return encoded_jwt
        
    except Exception as e:
        logger.error(f"❌ create_access_token: Ошибка создания токена: {str(e)}")
        import traceback
        logger.error(f"   Traceback: {traceback.format_exc()}")
        raise


def decode_access_token(token: str):
    """
    Декодирование JWT токена с логированием
    """
    try:
        logger.info("🔓 decode_access_token: Декодирование токена")
        logger.info(f"   Token length: {len(token)}")
        logger.info(f"   Token (first 30 chars): {token[:30]}...")
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        logger.info(f"   Payload decoded: {payload}")
        
        logger.info("✅ decode_access_token: Токен успешно декодирован")
        return payload
        
    except JWTError as e:
        logger.warning(f"⚠️ decode_access_token: JWT ошибка: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"❌ decode_access_token: Неожиданная ошибка: {str(e)}")
        import traceback
        logger.error(f"   Traceback: {traceback.format_exc()}")
        return None
