from pydantic_settings import BaseSettings
from pydantic import BaseModel, model_validator, Field
from typing import Literal




class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int 
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    
    DATABASE_URL: str = None
    SECRET_KEY: str 
    ALGORITHM: str = 'HS256'

    # @model_validator(mode='before')
    # def get_database_url(cls, values):
    #     values['DATABASE_URL'] = f'postgresql+asyncpg://{values["DB_USER"]}:{values["DB_PASS"]}@{values["DB_HOST"]}:{values["DB_PORT"]}/{values["DB_NAME"]}'
    #     return values
    

    @model_validator(mode='before')
    def get_database_url(cls, values):
        values['DATABASE_URL'] = f'postgresql+asyncpg://{values["DB_USER"]}:{values["DB_PASS"]}@db:{values["DB_PORT"]}/{values["DB_NAME"]}'
        return values


    TEST_DB_HOST: str
    TEST_DB_PORT: int
    TEST_DB_USER: str = 'default_user'
    TEST_DB_PASS: str
    TEST_DB_NAME: str
    

    @model_validator(mode='before')
    def get_TEST_database_url(cls, values):
        values['TEST_DATABASE_URL'] = f'postgresql+asyncpg://{values["TEST_DB_USER"]}:{values["TEST_DB_PASS"]}@{values["TEST_DB_HOST"]}:{values["TEST_DB_PORT"]}/{values["TEST_DB_NAME"]}'
        return values


    MODE: Literal['DEV', 'TEST', 'PROD'] #тест аактивируется при запуске путеста


    TEST_DATABASE_URL: str = None


    REDIS_HOST:str
    REDIS_PORT:int 


    class Config: 
    # class ConfigDict: 
        env_file = '.env'

settings = Settings()   
