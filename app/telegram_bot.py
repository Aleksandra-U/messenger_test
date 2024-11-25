import logging 
import asyncio 
import requests 
from aiogram import Bot, Dispatcher, types 
from aiogram.filters import Command

from app.models import Users

from app.database import async_session_maker

from sqlalchemy import select


#2. если recipient с таким id получает сообщение и у него нет токена - отправить сообщение 


# 7586292019:AAHChEgA_fkbVNNXr71VumfWlob2RAMMkIk

API_TOKEN = '7586292019:AAHChEgA_fkbVNNXr71VumfWlob2RAMMkIk' 
 
bot = Bot(token=API_TOKEN) 
dp = Dispatcher() 



@dp.message(Command('start'))
async def start_work(messages: types.Message): 
    await messages.reply('Напишите свой логин в приложении мессенджер')



@dp.message() 
async def get_login(message: types.Message): 
    user_name_from_message = message.text 

    chat_id_user = message.from_user.id

    async with async_session_maker() as session: 
        user_result = await session.execute(select(Users).filter(Users.user_name == user_name_from_message))
        user = user_result.scalars().first()

        if user:
            user.telegram_id = chat_id_user
            await session.commit() 
            await message.reply('Ваш ID успешно зарегестрирован')
        else:    
            await message.reply('Пользователь с таким логином не найден')


async def main_telegram(): 
    logging.basicConfig(level=logging.INFO) 
    await dp.start_polling(bot) 