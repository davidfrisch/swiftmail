from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLITE3_DATABASE_URL = "sqlite:///./sqlalchemy_example.db"
# POSTGRESQL_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432"

engine = create_engine(SQLITE3_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


