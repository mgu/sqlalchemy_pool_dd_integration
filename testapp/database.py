from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import ddtrace_sqlalchemy_pool

ddtrace_sqlalchemy_pool.patch()

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:secret@127.0.0.1:5432/postgres"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, pool_size=1, max_overflow=5, pool_recycle=20, pool_pre_ping=True
)
ddtrace_sqlalchemy_pool.trace_pool(engine.pool)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
