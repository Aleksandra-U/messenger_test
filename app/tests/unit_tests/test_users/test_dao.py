

#ТЕКСТИРУЕМ ДАО - SQL алхимию. смотрим что она верно все отдает . инит тест с sql алхимией 


from app.communication.dao import UsersDAO
from httpx import AsyncClient
import pytest

#ТЕСТИРОВАНИЕ ЭНДПОИНТОВ 

@pytest.mark.parametrize('user_id, user_name, is_present', [
    (1, 'jessi', True),
    (2, 'Vova', True),
    (3, 'jjjj', False)
]) 
async def test_find_user_by_id(user_id, user_name, is_present):
    user = await UsersDAO.find_by_id(user_id)

    print(user)

    if is_present:
        assert user
        assert user.id == user_id 
        assert user.user_name == user_name  #проверить что юзер равен такому то 
    else:
        assert not user
    