from passlib.context import CryptContext
# from hashlib import bcrypt 

from pydantic import BaseModel #EmailStr
from app.communication.dao import UsersDAO

from jose import jwt
from datetime import datetime, timedelta, timezone

from app.config import settings


# хеширование пароля и проверка при входе после регистрации 
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def get_password_hash(password):
    return pwd_context.hash(password)

#проверка что пароль соответствует хешированной версии 
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)    


#функция для создания токена
def create_access_token(data:dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=3)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, settings.ALGORITHM
    )	
    return encoded_jwt



# получаем пользователя
async def authenticate_user(user_name:str, password:str): #email: EmailStr 
    user = await UsersDAO.find_one_or_none(user_name=user_name)
    if user is None or not verify_password(password, user.password): #user.hashed_password
        return None
    return user