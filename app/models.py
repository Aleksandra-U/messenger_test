
from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key= True, nullable=False, autoincrement=True) 
    user_name = Column(String, nullable=False) 
    password = Column(String, nullable=False) 
    telegram_id = Column(Integer, nullable=False, default=0)
    token = Column(Integer, nullable=False, default=0)

    def __str__(self):
        return f'Пользователь {self.user_name}'


class Messages(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key= True, autoincrement=True)
    sender = Column(ForeignKey('users.id'))
    recipient = Column(ForeignKey('users.id'))
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
