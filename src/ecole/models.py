from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import CheckConstraint, Column, Integer
from sqlmodel import Field, Relationship, SQLModel


def _utcnow() -> datetime:
    return datetime.now(UTC)


class SongStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    PRIVATE = "private"


class GenreBase(SQLModel):
    name: str = Field(index=True, min_length=1, max_length=100)


class Genre(GenreBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    albums: list["Album"] = Relationship(back_populates="genre")


class AlbumBase(SQLModel):
    name: str = Field(index=True, min_length=1, max_length=200)
    genre_id: int = Field(foreign_key="genre.id", index=True)


class Album(AlbumBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    updated_at: datetime = Field(default_factory=_utcnow)
    genre: Genre | None = Relationship(back_populates="albums")
    songs: list["Song"] = Relationship(back_populates="album")


class SongBase(SQLModel):
    name: str = Field(index=True, min_length=1, max_length=200)
    duration: int = Field(
        sa_column=Column(Integer, CheckConstraint("duration >= 0"), nullable=False),
        ge=0,
        description="Duree en secondes",
    )
    status: SongStatus = Field(default=SongStatus.DRAFT, index=True)
    album_id: int = Field(foreign_key="album.id", index=True)


class Song(SongBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utcnow)
    album: Album | None = Relationship(back_populates="songs")
