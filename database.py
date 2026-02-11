from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # this is SQLite specific
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)  # creates database sessions


class Base(DeclarativeBase):
    pass


def get_db():
    # dependency function; provides a database session to path operations
    # ensures proper opening and closing of sessions
    with SessionLocal() as db:  # ensures cleanup even if an error occurs
        yield db
