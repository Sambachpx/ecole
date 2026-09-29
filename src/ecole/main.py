from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ecole.admin import setup_admin
from ecole.models import Base
from ecole.seed import is_empty, seed

# Connect to DB
engine = create_engine("sqlite:///./app.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Create tables + seed data
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if is_empty(db):
            seed(db)
    yield
    engine.dispose()


app = FastAPI(lifespan=lifespan)

admin = setup_admin(app, engine)


def get_db() -> Iterator[Session]:
    """Helper to access a DB session in FastAPI"""
    with SessionLocal() as db:
        yield db


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/users/{user_id}")
def read_user(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    q: str | None = None,
):
    return {"user_id": user_id, "q": q}
