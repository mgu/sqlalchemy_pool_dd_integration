import time
from fastapi import FastAPI
from sqlalchemy import text
from pydantic import BaseModel

from .database import SessionLocal

app = FastAPI()


class ReturnSchema(BaseModel):
    status: str

@app.get("/")
def read_root() -> ReturnSchema:
    with SessionLocal() as session:
        result = session.execute(text("SELECT 2"))
        session.rollback()
    return {"status": "OK"}
