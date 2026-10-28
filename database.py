from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite дерекқорын құру (server.db деген файл пайда болады)
SQLALCHEMY_DATABASE_URL = "sqlite:///./server.db"

# check_same_thread=False - FastAPI-дің бірнеше сұранысты қатар өңдеуі үшін керек
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()