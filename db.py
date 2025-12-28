import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


engine = create_async_engine(
    os.getenv("DATABASE_URL"),
    echo=True,
    future=True,
)

async_session = async_sessionmaker(engine, expire_on_commit=False)
