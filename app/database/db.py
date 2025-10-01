import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import declarative_base

load_dotenv(override=True)

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# URL подключения к базе данных
DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}"

engine = create_async_engine(
    DATABASE_URL, 
    echo=True,
    # Настройки для правильной работы с Unicode
    connect_args={
        # Дополнительные настройки для asyncpg
        "command_timeout": 60,
        "server_settings": {
            "jit": "off"
        }
    },
    # Дополнительные настройки для PostgreSQL
    pool_pre_ping=True,
    pool_recycle=300,
    # Настройки для правильной работы с Unicode в SQLAlchemy
    echo_pool=True
)

async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()

# Dependency
