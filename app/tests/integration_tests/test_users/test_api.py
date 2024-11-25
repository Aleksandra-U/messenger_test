
# def test_abc():
#     assert 1 == 1


from httpx import AsyncClient
import pytest


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text



# #ТАК ВООБЩЕ ПОСЛЕ КАЖДОГО ТЕСТА ОБНУЛЯЕТСЯ 
# # @pytest.fixture(autouse=True)
# # async def reset_database(session: AsyncSession):
# #     # Очистка таблицы users перед каждым тестом
# #     await session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
# #     await session.commit()



# # #ТЕСТИРОВАНИЕ ЭНДПОИНТОВ 

# # @pytest.mark.parametrize('user_name, password, password_repeat, status_code', [
# #     # ('jessy', '1', '1', 200),
# #     # ('vova', '1', '1', 200),
# #     # ('otis', '1', '1', 200),
# #     #('jessy', '2', '2', 409)
        # ('jessi', '1', '1', 200),
        # ('jessi', '1', '1', 409)

# # ])
# # async def test_register_user(user_name, password, password_repeat, status_code, ac: AsyncClient):
# #     response = await ac.post('/register', data={
# #         'user_name': user_name,
# #         'password': password, 
# #         'password_repeat': password_repeat,
# #     } )

# #     print('JOPA')
# #     print(response.text)

# #     assert response.status_code == status_code

    




# функция verify_password из библиотеки Passlib не может 
# распознать хэш пароля, который вы передаете. В частности, 
# ошибка UnknownHashError: hash could not be identified говорит о том, 
# что Passlib не знает, каким образом обработать предоставленный хэш.

# @pytest.mark.parametrize('user_name, password, status_code', [
#     ('jessi', '1', 200),
#     ('Vova', '1', 200)
# ])
# async def test_login_user(user_name: str, password: str, status_code, ac: AsyncClient):
#     response = await ac.post('/', data={  #не json 
#         'user_name': user_name,
#         'password': password, 
#     } )

#     print(response)
    
#     assert response.status_code == status_code


# # # # для get запросов params 
# # # # для post запросов json  





# # # # интеграционное терсторование через бд 
