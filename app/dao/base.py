from app.database import async_session_maker

from sqlalchemy.orm import aliased 

from sqlalchemy import select, insert

class BaseDAO:
    model = None
    
    @classmethod
    async def find_by_id(cls, model_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).filter(cls.model.id == model_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        
    @classmethod
    async def find_all(cls, **filters):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filters)
            result = await session.execute(query)
            return result.scalars().all()    
        
    @classmethod
    async def find_without_me(cls, curr_id:int):
        async with async_session_maker() as session:
            query = select(cls.model).filter(cls.model.id != curr_id)
            result = await session.execute(query)
            return result.scalars().all()    
        

    @classmethod
    async def find_one_or_none(cls, **filters):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filters)
            result = await session.execute(query)
            return result.scalar_one_or_none()     
        

    @classmethod
    async def add(cls, **data): 
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data)
            await session.execute(query)
            await session.commit() 

            query = select(cls.model).filter_by(**data)
            result = await session.execute(query)
            return result.scalar()
        
    @classmethod 
    async def update_token(cls, user_id: int, token_value: int): 
        async with async_session_maker() as session: 
            user = await session.get(cls.model, user_id) 
            if user: 
                user.token = token_value 
                await session.commit()      