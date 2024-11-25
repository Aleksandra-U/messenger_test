from fastapi import Request, Depends
from jose import jwt, JWTError
from datetime import datetime,timezone
from app.communication.dao import UsersDAO

from app.config import settings


from app.exceptions import UserIsNotPresentException, IncorrectFormatTokenException, TokenAbsentException, TokenExpiredException

def get_token(request: Request): #пользовательский запрос существует только 
     #в рамках эндпоинта  
    #  функция с реквстом если используется в другой фунции 
    #  должны дойти на верхний уровень до эндпоинта 
    token = request.cookies.get('booking_access_token')
    if not token:
        raise TokenAbsentException
    return token #отсюда для get_current_user берутся данные про пользователя 

# token = get_token() так нельзя токен добыть. и потом сюда ниже передать.  


async def get_current_user(token: str = Depends(get_token)):
    try:  
        #говорит не интересен хедер и подпись. но тут что?!?!?!?
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )	
    except JWTError:
        raise IncorrectFormatTokenException
    expire: str = payload.get('exp') 
    if (not expire) or (int(expire) < datetime.now(timezone.utc).timestamp()):
        raise TokenExpiredException
    user_id: str = payload.get('sub')
    if not user_id:
        raise UserIsNotPresentException
    user = await UsersDAO.find_by_id(int(user_id))
    if not user:
        raise UserIsNotPresentException
    return user #возвращает из бд этого пользователя, который запрашивает страницы. 
    # если он есть 
    # ВОЗВРАЩАЕТСЯ МОДЕЛЬ ПОЛЬЗОВАТЕЛЯ 