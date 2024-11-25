from app.dao.base import BaseDAO
from app.models import Users, Messages

from app.database import async_session_maker

from sqlalchemy import select, insert, or_, and_

from datetime import datetime



import asyncio

class UsersDAO(BaseDAO): 
    model = Users

    @classmethod
    async def get_user_name_by_id(cls, user_id : int):
        async with async_session_maker() as session: 
            query = (select(Users).filter(Users.id == user_id))
            result = await session.execute(query) 
            return result.scalars().first().user_name


class MessagesDAO(BaseDAO): 
    model = Messages

    @classmethod 
    async def get_conversation_users(cls, user_id: int): 
        async with async_session_maker() as session: 
            # Выбираем пользователей, которые отправили или получили сообщение от текущего пользователя 
            query = (
                select(Users) 
                .join(Messages, or_(Messages.sender == Users.id, Messages.recipient == Users.id)) 
                .filter(or_(Messages.sender == user_id, Messages.recipient == user_id)) 
                .filter(Users.id != user_id)
                .distinct(Users.id)  # Убираем дубликаты, если одно и то же сообщение уже было учтено 
            ) 
 
            result = await session.execute(query) 
            return result.scalars().all()
        

            # users = result.scalars().all()
            # return users
        



    #получаю сообщения между двумя пользователями
    @classmethod 
    async def get_messages_between_users(cls, user_id: int, other_user_id: int): 
        async with async_session_maker() as session: 
            # Выбираем сообщения между двумя пользователями и сортируем их по времени 
            query = ( 
                select(Messages, 
                    Users.user_name.label('sender_username'))
                .outerjoin(Users, Messages.sender == Users.id)
                .filter( 
                    or_( 
                        and_(Messages.sender == user_id, Messages.recipient == other_user_id), 
                        and_(Messages.sender == other_user_id, Messages.recipient == user_id) 
                    ) 
                ) 
                .order_by(Messages.timestamp)  # Сортировка по времени 
            ) 

            result = await session.execute(query) 
            messages = []
            for message, sender_username in result.all():
                messages.append((message.message, sender_username, message.timestamp.strftime("%H:%M")))
            
            return messages  # Возвращаем все сообщения как список словарей

            # messages = result.scalars().all()
            # #преобразую сообщения в словари
            # return [{"id": msg.id, 'sender': msg.sender, 'recipient': msg.recipient, "message": msg.message, "timestamp": msg.timestamp} for msg in messages]
        


    #метод сохраняет отпраленные сообщения 
    @classmethod 
    async def put_message_to_db(cls, sender_id: int, recipient_id: int, message: str): 
        #id = 1 убрала. мб автоматически будет? 
        new_message = cls.model(sender=sender_id, recipient=recipient_id, message=message, timestamp=datetime.now()) 
        async with async_session_maker() as session: 
            session.add(new_message) 
            await session.commit()    


            # CREATE TABLE messages ( 
            #     id SERIAL PRIMARY KEY, 
            #     sender INTEGER, 
            #     recipient INTEGER, 
            #     message VARCHAR, 
            #     timestamp TIMESTAMP WITHOUT TIME ZONE 
            # );