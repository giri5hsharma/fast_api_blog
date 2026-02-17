from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
 
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # this is SQLite specific
)

AsyncSessionLocal = async_sessionmaker(   
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)  # creates database sessions


class Base(DeclarativeBase):
    pass


async def get_db(): #CONVERTED TO ASYNC FUNCTION
    # dependency function; provides a database session to path operations
    # ensures proper opening and closing of sessions
    async with AsyncSessionLocal() as session:  # ensures cleanup even if an error occurs
        yield session
