from fastapi import FastAPI
import asyncio
from app.telegram_bot import main_telegram

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from redis import asyncio as aioredis


from contextlib import asynccontextmanager


from app.communication.router import router as router_messages

app = FastAPI()


app.include_router(router_messages)

asyncio.ensure_future(main_telegram())
