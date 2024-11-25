from fastapi import APIRouter, Request, Form, Response, Depends, requests
from fastapi.templating import Jinja2Templates
from typing import List, Dict
import json
from redis import asyncio as aioredis
import json
from datetime import datetime
from sqlalchemy import select, insert, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession 
from app.communication.dao import UsersDAO, MessagesDAO
from fastapi.responses import RedirectResponse
from app.models import Users, Messages
from app.database import async_session_maker
from app.communication.auth import get_password_hash, authenticate_user, create_access_token
from app.communication.dependencies import get_token, get_current_user 
from fastapi import WebSocket, WebSocketDisconnect
from app.tasks.tasks import send_msg_task
from fastapi import HTTPException
from app.exceptions import UserAlreadyExistsException

router = APIRouter(
    tags=['Фронтэнд']
)



templates = Jinja2Templates(directory='app/templates')


# тут условие тк  это менеджер вебсокетов. он отбирает сообщения которые прилетают в бродкаст 
class ConnectionManager:
    def __init__(self):
        #это словарь кто общается 
        self.active_connections: dict[int, WebSocket] = {} #в этом словаре находятся все активные пользователит по id из бд 


    async def connect(self, user_id: int, other_id: int, websocket: WebSocket): #прописать пользователя с которым переписываюь. 
        # иначе если открою диалог напрмиер с джесси - перезапишу этот вебсокет !!!!!!!!!!!!!!!!!!!!!
        await websocket.accept()
        print(f"До")
        print(self.active_connections)


        # Если ключа нет, создаем новый список
        if user_id not in self.active_connections:
            # словарь, где ключ — это user_id, а значение — список
            #ЭТО СЛОВАРЬ С КЕМ ОБЩАЮТСЯ 
             self.active_connections[user_id] = {}
             #     self.active_connections[user_id] = [other_id, websocket]

         # тут добавляется новый ключ other_id в словарь по моему ключу + 
         #и добавляется значение ко второму ключу - websocket
        self.active_connections[user_id][other_id] = websocket


        #active_connections - сюда записываются люди которые зашли на сайт 

        print('После')
        print(self.active_connections)


        # задание:  придумать способ как сохранять к одному юзеру много разных диалогов одновременно 
        # и при отправке соощений отправляется в конкретный диалог 

# {
#     'user_id_1' : [other_id, websocket], [other_id, websocket]
#     'user_id_2' : [other_id, websocket]
# }



    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]


    async def broadcast(self, message: str, sender_id: int, recipient_id: int):
        print(f"Active connections {self.active_connections}")

        #нужно отсылать в тот вебсокет с конкретнымы пользователем !!!!!!!!!!

        await self.active_connections[sender_id][recipient_id].send_text(message)


        #проверяем у человека которому м ыотослали открыт ли диалог. вот у этого recipient_id 
        # и проверяем открыт ли у него диалог с нами. если октрыт отпарвляем сообщения 
        if recipient_id in self.active_connections and sender_id in self.active_connections[recipient_id]:
            await self.active_connections[recipient_id][sender_id].send_text(message)

        # if recipient_id in self.active_connections



        # то есть recipient_id есть ключе 5 
        # conn = {
        #         5: { 2: 10, 
        #             4: 30

        #         }
        #     }


        # то есть 

        # sender_id in self.active_connections[recipient_id]: 
        # есть в ключе 2 


        #         conn = {
        #         5: { 2: 10, 
        #             4: 30

        #         }
        #     }




        # if sender_id in self.active_connections: 
        #     for val_sen in self.active_connections[sender_id]:
        #         if recipient_id == val_sen[0]:
        #             connection_send = val_sen[1]
        #             await connection_send.send_text(message)

        # if recipient_id in self.active_connections: 
        #     for val_sen in self.active_connections[recipient_id]:
        #         if sender_id == val_sen[0]:
        #             connection_send = val_sen[1]
        #             await connection_send.send_text(message)



        # #разбила словарь на ключ и значение. user_id \ other_id, websocket
        # for key, val in self.active_connections.items(): #это кортежи (key, val) int  и список списков 
        #     #если отпавитель есть
        #     if sender_id == key:
        #         #иду циклом по списку списков значения ключа, где записаны id получателя и websocket
        #         for obj in val:
        #             #если получатель есть 
        #             if recipient_id == obj[0]:
        #                 # Получаем websocket
        #                 connection_send = obj[1]
        #                 await connection_send.send_text(message)


        #     #если получатель есть
        #     if recipient_id == key:
        #         #иду циклом по списку списков значения ключа, где записаны id отправителя и websocket
        #         for obj in val:
        #             #если отправитель есть 
        #             if sender_id == obj[0]:
        #                 # Получаем websocket
        #                 connection_rec = obj[1]
        #                 await connection_rec.send_text(message)
            


# {1: [[3, <starlette.websockets.WebSocket object at 0x000001D9AC4CE990>], [2, <starlette.websockets.WebSocket object at 0x000001D9AC7142B0>]]}
 



manager = ConnectionManager()


async def send_msg(chat_id, text): 
    send_msg_task.delay(chat_id, text)  # Отправка задачи в очередь





# vova_id = '1308606032'
# veniamin_id = '2021236462'

# def send_msg(chat_id, text):
#     token = '6776584532:AAHUsn2wWvjK6WEIA0zLTOPG2icJjFFN9eE'
#     url_req = 'https://api.telegram.org/bot' + token + '/sendMessage' + '?chat_id=' + chat_id + '&text=' + text
#     result = requests.get(url_req)




#роутер  для общения между двумя пользователями в реальном времени.
#Redis используется для кэширования сообщений
@router.websocket("/ws/{user_id}/{other_id}") #эти тут из шаблона message_page
    # в шаблон message_page они попадают из эндпоинта get_messages
async def websocket_endpoint(websocket: WebSocket, user_id: int, other_id: int):
    await manager.connect(user_id, other_id, websocket)  # Обратите внимание, что аргументы теперь оба передаются
    
    # редис - соварь
    # можно по клюу поместить значение и можно по ключу получить значение
    #redis = await get_redis() устанавливает соединение с Redis.

    # получаю словарь в виде редис с эндпоинте
    redis = await get_redis()

    try:
        while True:

            # Получение сообщение в переменную message
            # тут метод блокирует выполнение до тех пор, 
            # пока не будет получено сообщение от пользователя.
            message = await websocket.receive_text()
            print(message, user_id, other_id)


            # есть сообщение message
            # и два ключа user_id other_id и все их сообшения

            user_name = await UsersDAO.get_user_name_by_id(user_id)

            # Кэширование сообщений:
            # внутир Вовина логика чтобы не хранить два дубликата переписки
            cache_key = f"messages:{user_id}:{other_id}" if user_id < other_id else f"messages:{other_id}:{user_id}"
            
            # тут cache_key - ключ
            # получаем все сообщения по ключу cache_key из словаря redis . 
            # записываем в переменную  cached_message
            cached_messages = await redis.get(cache_key)
            
            # дальше проверка есть вообще сообщения или нет if cached_message

            # Если кэш существует, он загружается и преобразуется из 
            # JSON в Python-объект (список сообщений). 

            # если сообщение есть - сериаизую сзначение loads 
            # (в редисе хранится все в стр в строке) . 
            # Loads переводит стркоу в тип данных питона
            if cached_messages:
                messages = json.loads(cached_messages)

                #БЕРУ ИЗ КЭШИ И ИЗ JSON ПЕРЕВОЖУ В НОРМАЛЬНОЕ СООБЩЕНИЕ. В ЛЮБОЙ ТИП ДАННЫХ ПИТОНА. ТУТ СПИСОК ДОЛЖЕН БЫТЬ 

                # Эта функция используется для десериализации (преобразования) 
                # строки в формате JSON обратно в объект Python (например, в словарь).
            
                # это необходимо, когда вы получаете данные в виде строки JSON 
                # и хотите работать с ними как с обычными объектами Python.

                # Здесь строка cached_messages, содержащая предыдущие сообщения 
                # в формате JSON, преобразуется обратно в объект Python (вероятно, 
                # в список или словарь), чтобы вы могли с ним работать, например, 
                # для отображения сообщений на интерфейсе пользователя.

            # Если кэш отсутствует, то есть сообщений нет 
            # создается пустой список messages = []. возвращается пустой список 
            else:
                messages = []

            # перевестииз строки в другой тип данных loads
            # '[6,2,7]'

            # дальше я в этот список messages добавляю новое сообщение message имя  дату
            messages.append((message, user_name, datetime.now().strftime("%H:%M")))

            # и в словарь redis по ключу cache_key добавляем messages+ dumps 
            # сериализмция (перевод в строку)  + указываю что 10 минут данные в кеше

            # Сохранение нового сообщения в кэш: 
            # После добавления нового 
            # сообщения в список, обновленный список сообщений снова сохраняется 
            # в Redis с помощью await redis.set(cache_key, json.dumps(messages), ex=600), 
            # где ex=600 означает, что данные будут храниться в кэше 10 минут.
            await redis.set(cache_key, json.dumps(messages), ex=600)

            #КЭЩ ПРИНИМАЕТ ТОЛКЬО JSON !!!!!!!!!

            await MessagesDAO.put_message_to_db(sender_id=user_id, recipient_id=other_id, message=message)

            telegram_message = f'Вам пришло сообщение от {user_name}. Сообщение:{message}'

            async with async_session_maker() as session: 
                telegram_id_result = await session.execute(select(Users.telegram_id).filter(Users.id == other_id))
                telegram_id = telegram_id_result.scalars().first()

            async with async_session_maker() as session: 
                token_result = await session.execute(select(Users.token).filter(Users.id == other_id))
                check_token = token_result.scalars().first()

            if telegram_id and telegram_id != 0: 
                if check_token == 0:
                    await send_msg(telegram_id, telegram_message)

            # Отправляем сообщение только другому пользователю
            #await manager.send_personal_message(json.dumps({'user': user_name, 'timestamp': datetime.now().strftime("%H:%M"), 'message': message}), other_id)
            await manager.broadcast(json.dumps({'user': user_name, 'timestamp': datetime.now().strftime("%H:%M"), 'message': message}), user_id, other_id)

            #ЭТО СООБЩЕНИЕ ОТПРАВИТСЯ В БРОДКАСТ А ОТТУДА В HTML. HTTML - ПРИНИМАЕТ ТОЛЬКО JSON-ФОРМАТ 



            # message пришло из вебсокета js html / хотим вебсокету обратно отослать сообщения 
            # dumps -  видимо json формат исползутс для передаче в js  ???????

           
            # Вызов функции json.dumps(...): используется для сериализации
            #  (преобразования) объекта Python (в данном случае, словаря) 
            #  в строку в формате JSON.

            # Это нужно для того, чтобы передать данные в виде строки, например, 
            # через сеть или сохранить в файл. JSON — это стандартный формат 
            # обмена данными, который легко читается и используется в веб-разработке.

            # Здесь создается JSON-строка, содержащая информацию о пользователе,
            #  времени и сообщении, которую затем отправляют (или "широковещательно" 
            # транслируют) другим пользователям.



    except WebSocketDisconnect:
        manager.disconnect(user_id)
        await manager.broadcast(f"User {user_id} left the chat", user_id, other_id)
    except Exception as e:
        print(e)






@router.get("/main_page")
async def start_page(request: Request, user: Users = Depends(get_current_user)):
    conversation_users = await MessagesDAO.get_conversation_users(user_id=user.id)

    return templates.TemplateResponse("start_page.html", {"request": request, "conversation_users": conversation_users})
 



# Redis не выгружались данные до докера и потом после докера УКАЗАЛ ПРАВИЛЬНЫЕ АДРЕСА 
async def get_redis():
    redis = aioredis.from_url("redis://cache:6379") #так писать если докер на компе запускаю 
    return redis

# получаю объект redis. переменная хранилище где находятся все данные 
# async def get_redis():
#     redis = aioredis.from_url("redis://localhost:6379")
#     return redis 




# роутер для получения сообщений между пользователями.
#Redis тут используется для кэширования сообщений

@router.get("/messages/{other_user_id}") 
async def get_messages(request: Request, other_user_id: int, user: Users = Depends(get_current_user)):  

    user_name = await UsersDAO.get_user_name_by_id(user.id)
    other_user_name = await UsersDAO.get_user_name_by_id(other_user_id)
    

    # редис - соварь
    # можно по клюу поместить значение и можно по ключу получить значение
    #redis = await get_redis() устанавливает соединение с Redis.

    #получаю словарь в виде редис с эндпоинте
    redis = await get_redis()


    # тут сообщения как в вебскете НЕТ во такого 
    # message = await websocket.receive_text()

    # НО ЕСТЬ два ключа user_id other_id и все их сообшения

        # Кэширование сообщений:
    # внутир Вовина логика чтобы не хранить два дубликата переписки
    cache_key = f"messages:{user.id}:{other_user_id}" if user.id < other_user_id else f"messages:{other_user_id}:{user.id}"
    
    
    # cache_key - ключ
    # Получаем все сообщения по ключу cache_key из словаря redic . записываем в переменную  cached_message
    cached_messages = await redis.get(cache_key)

    # дальше прверка есть вообще сообения или нет if cached_message
    # если сообщение есть в кэше - сериаизую сзначение loads 
    # (в редисе хранится все в стр в строке)
    # Loads переводит стркоу в тип данных питона
    if cached_messages:
        # перевестииз строки в другой тип данных loads
        messages = json.loads(cached_messages)

        # если сообщений нет беру сообщения из базы данных 
    else:
        messages = await MessagesDAO.get_messages_between_users(user_id=user.id, other_user_id=other_user_id)


    # и в словарь redis по ключу cache_key добавляем messages+ 
    # dumps сериализмция (перевод в строку)  + указываю что 1- минут данные в кеше

        await redis.set(cache_key, json.dumps(messages), ex=600) 



    return templates.TemplateResponse("message_page.html", { 
        "request": request, 
        "messages": messages,
        'user_name' : user_name, 
        "other_name": other_user_name,  # Отправляем id другого пользователя 
        'user_id' : user.id,
        'other_id': other_user_id,
        'user': user
    })






@router.post("/send_message") 
async def send_message(recipient_id: int = Form(...), message: str = Form(...), user: Users = Depends(get_current_user)): 
    await MessagesDAO.put_message_to_db(sender_id=user.id, recipient_id=recipient_id, message=message) 
    return RedirectResponse(url=f"/messages/{recipient_id}", status_code=303)




@router.get("/all_users")
async def all_users(request: Request, user: Users = Depends(get_current_user)):

    async with AsyncSession() as session: 
        async with session.begin():
            users = await UsersDAO.find_without_me(user.id)  
                
            return templates.TemplateResponse("users.html", {"request": request, "users": users})
        




@router.get("/") 
async def login_form(request: Request, error_message: str = None):
    return templates.TemplateResponse("register_and_auth.html", {"request": request, "error_message": error_message})




@router.post("/")
async def login_user(request: Request, response: Response, user_name: str = Form(...), password: str = Form(...)):
    # получаем пользователя
    user = await authenticate_user(user_name, password)
    if not user:
        # Возвращаем форму входа с сообщением об ошибке 
        return templates.TemplateResponse("register_and_auth.html", { 
            "request": request,  
            "error_message": "Неправильный логин или пароль", 
        })
        
    access_token = create_access_token({'sub': str(user.id)}) 

    await UsersDAO.update_token(user.id, 1)


    response = RedirectResponse(url='/main_page', status_code=303)
    response.set_cookie('booking_access_token', access_token, httponly=True)


    return response









@router.post("/register") 
async def register_user(request: Request, user_name: str = Form(...), password: str = Form(...), 
                        password_repeat: str = Form(...), 
): 

    async with AsyncSession() as session: 
        async with session.begin():
    # смотрим, есть ли такой юзер. если есть - вернем ошибку 
            existing_user = await UsersDAO.find_one_or_none(user_name=user_name)
            if existing_user:
                # raise HTTPException(status_code=409, detail="Пользователь с таким user_name уже существует")
                # raise UserAlreadyExistsException #ПРИ ТЕСТИРОВАНИИ
                return templates.TemplateResponse("register_and_auth.html", { 
                    "request": request,  
                    "error_message": "Пользователь с таким user_name уже существует" 
                })


            if password != password_repeat: 
                return templates.TemplateResponse("register_and_auth.html", { 
                    "request": request, 
                    "error_message": "Пароли не совпадают" 
                }) 

            hashed_password = get_password_hash(password) 
            await UsersDAO.add(user_name=user_name, password=hashed_password, telegram_id=0) 


            return templates.TemplateResponse("register_and_auth.html", { 
                "request": request, 
                "success_message": "Вы успешно зарегистрированы!" 
            })







@router.post('/logout') #response_class=HTMLResponse
async def logout_user(response: Response, request: Request): 

    token = get_token(request)  # Получаем токен, если он существует 
    user = await get_current_user(token)  # Получаем текущего пользователя по токену

    # Устанавливаем значение токена в базе данных для пользователя на 0 
    await UsersDAO.update_token(user.id, 0)

    response = RedirectResponse(url='/', status_code=303) 
    response.delete_cookie('booking_access_token')
    return response