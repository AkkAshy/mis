from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, Token
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
import logging
import traceback

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Регистрация нового пользователя с детальным логированием
    """
    try:
        logger.info("=" * 80)
        logger.info("🔵 НАЧАЛО РЕГИСТРАЦИИ ПОЛЬЗОВАТЕЛЯ")
        logger.info(f"📝 Username: {user.username}")
        logger.info(f"📝 Email: {user.email}")
        logger.info(f"📝 Full name: {user.full_name}")
        logger.info(f"📝 Role: {user.role}")
        logger.info(f"📝 Password length: {len(user.password) if user.password else 0} chars")
        
        # Шаг 1: Проверка username
        logger.info("🔍 Шаг 1: Проверка существования username...")
        try:
            db_user = db.query(User).filter(User.username == user.username).first()
            if db_user:
                logger.warning(f"⚠️ Username '{user.username}' уже зарегистрирован")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Username '{user.username}' already registered"
                )
            logger.info("✅ Username свободен")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Ошибка при проверке username: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Database error checking username: {str(e)}")
        
        # Шаг 2: Проверка email
        logger.info("🔍 Шаг 2: Проверка существования email...")
        try:
            db_user = db.query(User).filter(User.email == user.email).first()
            if db_user:
                logger.warning(f"⚠️ Email '{user.email}' уже зарегистрирован")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Email '{user.email}' already registered"
                )
            logger.info("✅ Email свободен")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Ошибка при проверке email: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Database error checking email: {str(e)}")
        
        # Шаг 3: Хеширование пароля
        logger.info("🔐 Шаг 3: Хеширование пароля...")
        try:
            logger.info(f"   Password type: {type(user.password)}")
            logger.info(f"   Password value (first 5 chars): {str(user.password)[:5]}...")
            
            hashed_password = get_password_hash(user.password)
            
            logger.info(f"   Hashed password length: {len(hashed_password)}")
            logger.info(f"   Hashed password (first 20 chars): {hashed_password[:20]}...")
            logger.info("✅ Пароль успешно захеширован")
        except Exception as e:
            logger.error(f"❌ Ошибка при хешировании пароля: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Password hashing error: {str(e)}")
        
        # Шаг 4: Создание объекта пользователя
        logger.info("👤 Шаг 4: Создание объекта пользователя...")
        try:
            db_user = User(
                username=user.username,
                full_name=user.full_name,
                email=user.email,
                hashed_password=hashed_password,
                role=user.role
            )
            logger.info(f"   User object created: {db_user}")
            logger.info("✅ Объект пользователя создан")
        except Exception as e:
            logger.error(f"❌ Ошибка при создании объекта пользователя: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"User object creation error: {str(e)}")
        
        # Шаг 5: Добавление в сессию БД
        logger.info("💾 Шаг 5: Добавление пользователя в БД...")
        try:
            db.add(db_user)
            logger.info("   User added to session")
            logger.info("✅ Пользователь добавлен в сессию")
        except Exception as e:
            logger.error(f"❌ Ошибка при добавлении в сессию: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Database session error: {str(e)}")
        
        # Шаг 6: Коммит в БД
        logger.info("💾 Шаг 6: Коммит изменений в БД...")
        try:
            db.commit()
            logger.info("   Commit successful")
            logger.info("✅ Изменения сохранены в БД")
        except Exception as e:
            logger.error(f"❌ Ошибка при коммите: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            db.rollback()
            logger.info("   Rollback executed")
            raise HTTPException(status_code=500, detail=f"Database commit error: {str(e)}")
        
        # Шаг 7: Обновление объекта
        logger.info("🔄 Шаг 7: Обновление объекта пользователя...")
        try:
            db.refresh(db_user)
            logger.info(f"   User ID: {db_user.id}")
            logger.info("✅ Объект обновлен")
        except Exception as e:
            logger.error(f"❌ Ошибка при обновлении объекта: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Не критично, продолжаем
        
        # Шаг 8: Создание токена
        logger.info("🔑 Шаг 8: Создание access token...")
        try:
            access_token = create_access_token(data={"sub": user.username})
            logger.info(f"   Token created (first 20 chars): {access_token[:20]}...")
            logger.info("✅ Токен создан")
        except Exception as e:
            logger.error(f"❌ Ошибка при создании токена: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Token creation error: {str(e)}")
        
        logger.info("=" * 80)
        logger.info("✅ РЕГИСТРАЦИЯ УСПЕШНО ЗАВЕРШЕНА")
        logger.info(f"   User ID: {db_user.id}")
        logger.info(f"   Username: {db_user.username}")
        logger.info(f"   Email: {db_user.email}")
        logger.info(f"   Role: {db_user.role}")
        logger.info("=" * 80)
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        # Пробрасываем HTTPException дальше
        raise
    except Exception as e:
        logger.error("=" * 80)
        logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА ПРИ РЕГИСТРАЦИИ")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        logger.error("=" * 80)
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected registration error: {str(e)}"
        )

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Вход пользователя с детальным логированием
    """
    try:
        logger.info("=" * 80)
        logger.info("🔵 НАЧАЛО ВХОДА ПОЛЬЗОВАТЕЛЯ")
        logger.info(f"📝 Username: {user.username}")
        logger.info(f"📝 Password length: {len(user.password) if user.password else 0} chars")
        
        # Шаг 1: Поиск пользователя
        logger.info("🔍 Шаг 1: Поиск пользователя в БД...")
        try:
            db_user = db.query(User).filter(User.username == user.username).first()
            if not db_user:
                logger.warning(f"⚠️ Пользователь '{user.username}' не найден")
                raise HTTPException(
                    status_code=400, 
                    detail="Incorrect username or password"
                )
            logger.info(f"✅ Пользователь найден (ID: {db_user.id})")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Ошибка при поиске пользователя: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        # Шаг 2: Проверка пароля
        logger.info("🔐 Шаг 2: Проверка пароля...")
        try:
            logger.info(f"   Input password type: {type(user.password)}")
            logger.info(f"   Stored hash length: {len(db_user.hashed_password)}")
            
            is_valid = verify_password(user.password, db_user.hashed_password)
            
            logger.info(f"   Password verification result: {is_valid}")
            
            if not is_valid:
                logger.warning(f"⚠️ Неверный пароль для пользователя '{user.username}'")
                raise HTTPException(
                    status_code=400, 
                    detail="Incorrect username or password"
                )
            logger.info("✅ Пароль верный")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Ошибка при проверке пароля: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Password verification error: {str(e)}")
        
        # Шаг 3: Создание токена
        logger.info("🔑 Шаг 3: Создание access token...")
        try:
            access_token = create_access_token(data={"sub": user.username})
            logger.info(f"   Token created (first 20 chars): {access_token[:20]}...")
            logger.info("✅ Токен создан")
        except Exception as e:
            logger.error(f"❌ Ошибка при создании токена: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Token creation error: {str(e)}")
        
        logger.info("=" * 80)
        logger.info("✅ ВХОД УСПЕШНО ЗАВЕРШЕН")
        logger.info(f"   User ID: {db_user.id}")
        logger.info(f"   Username: {db_user.username}")
        logger.info(f"   Role: {db_user.role}")
        logger.info("=" * 80)
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("=" * 80)
        logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА ПРИ ВХОДЕ")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        logger.error("=" * 80)
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected login error: {str(e)}"
        )
