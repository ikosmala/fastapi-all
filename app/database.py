from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import redis
from redis.retry import Retry
from redis.backoff import ExponentialBackoff
from redis.exceptions import BusyLoadingError, ConnectionError, TimeoutError
from .config import settings

# SQL Alchemy part
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Redis part
def get_rd():
    try:
        retry = Retry(ExponentialBackoff(), 3)
        rd = redis.Redis(
            host="redis",
            port=6379,
            decode_responses=True,
            retry=retry,
            retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError],
        )
        return rd
    except redis.RedisError as e:
        print(f"An error occurred: {e}")
