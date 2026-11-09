import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Дерекқор сілтемесін алу (Render-дегі Environment айнымалысынан немесе жергілікті SQLite-тен)
SQLALCHEMY_DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "sqlite:///./server.db"
)

# 2. Сілтемені SQLAlchemy үшін дұрыс форматқа келтіру
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

if SQLALCHEMY_DATABASE_URL.startswith("postgresql://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# 3. Қосылу параметрлері (тек Postgres үшін SSL керек)
connect_args = {"sslmode": "require"} if "postgres" in SQLALCHEMY_DATABASE_URL else {}

# 4. Двигательді (Engine) жасау
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()