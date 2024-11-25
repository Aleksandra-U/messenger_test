from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import NullPool

from app.config import settings



if settings.MODE  == 'TEST': 
    DATABASE_URL = settings.TEST_DATABASE_URL
    DATABASE_PARAMS = {'poolclass': NullPool}
else:
    DATABASE_URL = settings.DATABASE_URL   
    DATABASE_PARAMS = {}

# engine = create_async_engine(settings.DATABASE_URL,echo=True)
engine = create_async_engine(DATABASE_URL, **DATABASE_PARAMS) #диаимчески формируется 
#лбо текстовая среда либо сред разработки

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase): 
    pass








# engine = create_async_engine(settings.DATABASE_URL,echo=True)

# async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# class Base(DeclarativeBase):
#     pass
