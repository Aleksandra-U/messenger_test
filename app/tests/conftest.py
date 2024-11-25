import pytest

from app.config import settings

from app.database import Base, async_session_maker, engine 
#Base - акумулирует инфу всю,   
#async_session_maker - создание аиснхронных сессий 
#engine  - дижок чтобы подключиться к бд 
 
from app.models import Users, Messages

import json
import asyncio

from sqlalchemy import insert

from fastapi.testclient import TestClient 
from httpx import AsyncClient

from app.main import app as fastapi_app

from datetime import datetime 


# фикстура. функция которая подгот  авливает среду для тестирования 
# подъем бд, наполнение бд таблицаими , таблтцу данными 
# или часто переиспользуемые струкуры данных - словарик список . из можно отсюда возвращать 
# + фикстуры отдают через клдчевое слово yeld сессии - временные соединения 
# позволяют передать соединенеи , данные 





# @pytest.fixture(scope='function', autouse=True)
@pytest.fixture(scope='session', autouse=True)
async def prepare_database():
    assert settings.MODE == 'TEST' #убедиться что мод == тест 
    # чтто мы работает не с реальной бд , не с той что на локальнйо машине 

    async with engine.begin() as conn: #асинхронный контекстный менеджер / 
        #создает все таюлицы которы акумулированы в base 
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all) #тут хранистя инфа о всех столюцах 


    def open_mock_json(model: str):
        with open(f'app/tests/mock_{model}.json', encoding='utf-8') as file:
            return json.load(file)

        #вернуть все данные в формате json 

    users = open_mock_json('users')
    message = open_mock_json('message') #!!!!

    


    for mes in message:
        mes['timestamp'] = datetime.strptime(mes['timestamp'], "%Y-%m-%d %H:%M:%S.%f")




    # все данные вставлчяем в алхимию 
    async with async_session_maker() as session:
        add_users = insert(Users).values(users)
        add_messages = insert(Messages).values(message) 


        await session.execute(add_users) #исполнить запрос
        await session.execute(add_messages) #исполнить запрос

        await session.commit() #чтобы все данные оказались в базе 




@pytest.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()






@pytest.fixture(scope='function')
async def ac():
    async with AsyncClient(app=fastapi_app, base_url='http://test') as ac: #вызывает контекстный менеджер 
        yield ac #асинхронный клетнт. через йилд его отдаем польхуйтесь .
        #лля каждо функции создается заново 



# # использовать вот так
# def test_abc(ac):
#     await ac.get()



 
#передадим сессию как фикстуру 
@pytest.fixture(scope='function') #для каждой функции так отдельная сессия 
async def session():
    async with async_session_maker() as session:
        yield session
