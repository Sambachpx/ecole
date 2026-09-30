import os
import shutil
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, HTTPException, UploadFile
from pydantic import BaseModel, ConfigDict
from sqladmin import Admin
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from spotipy.admin import AlbumAdmin, GenreAdmin, SongAdmin
from spotipy.logic_metadata import extract_metadata
from spotipy.models import Base, Genre, Song, Status
from spotipy.seed import is_empty, seed

# Connect to DB
engine = create_engine("sqlite:///./app.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Create tables + seed data
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if is_empty(db):
            seed(db)
    yield
    engine.dispose()


app = FastAPI(lifespan=lifespan)

admin_app = Admin(app, engine)


def get_db() -> Iterator[Session]:
    """Helper to access a DB session in FastAPI"""
    with SessionLocal() as db:
        yield db


DbSession = Annotated[Session, Depends(get_db)]


@app.get("/")
def read_root() -> dict[str, str]:
    return {"Hello": "World"}


class GenreCreate(BaseModel):
    name: str


class GenreRead(GenreCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class SongCreate(BaseModel):
    name: str
    album_id: int
    duration: int = 0
    status: Status = Status.DRAFT


class SongRead(SongCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    file: str | None = None


@app.get("/genres", response_model=list[GenreRead])
def list_genres(db: DbSession) -> list[Genre]:
    return list(db.scalars(select(Genre).order_by(Genre.id)).all())


@app.post("/genres", response_model=GenreRead, status_code=201)
def create_genre(genre: GenreCreate, db: DbSession) -> Genre:
    new_genre = Genre(name=genre.name)
    db.add(new_genre)
    db.commit()
    db.refresh(new_genre)
    return new_genre


@app.post("/songs", response_model=SongRead, status_code=201)
def create_song(song: SongCreate, db: DbSession) -> Song:
    new_song = Song(
        name=song.name,
        album_id=song.album_id,
        duration=song.duration,
        status=song.status,
    )
    db.add(new_song)
    db.commit()
    db.refresh(new_song)
    return new_song


@app.get("/songs", response_model=list[SongRead])
def list_songs(db: DbSession) -> list[Song]:
    return list(db.scalars(select(Song).order_by(Song.id)).all())


@app.get("/albums/{album_id}/songs", response_model=list[SongRead])
def list_album_songs(album_id: int, db: DbSession) -> list[Song]:
    stmt = select(Song).where(Song.album_id == album_id).order_by(Song.id)
    return list(db.scalars(stmt).all())


@app.post("/songs/{song_id}/file", response_model=SongRead)
def song_upload_file(song_id: int, file: UploadFile, db: DbSession) -> Song:
    song = db.get(Song, song_id)
    if song is None:
        raise HTTPException(status_code=404, detail="Song not found")

    # Save file to uploads
    upload_dir = "uploads/songs/"
    os.makedirs(upload_dir, exist_ok=True)

    safe_name = Path(file.filename or "audio.mp3").name
    file_path = os.path.join(upload_dir, f"{song.id}_{safe_name}")
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Persist before calling the metadata micro-service
    # so the file is guaranteed to be available.
    song.file = file_path
    db.add(song)
    db.commit()
    db.refresh(song)

    try:
        name, duration = extract_metadata(file_path)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502, detail=f"Metadata service unavailable: {exc}"
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    # Save song
    song.duration = duration
    if name:
        song.name = name

    db.add(song)
    db.commit()
    db.refresh(song)
    return song


# Admin
admin_app.add_view(GenreAdmin)
admin_app.add_view(AlbumAdmin)
admin_app.add_view(SongAdmin)
