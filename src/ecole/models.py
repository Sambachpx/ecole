from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class SongStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    PRIVATE = "private"


class Genre(Base):
    __tablename__ = "genre"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)

    albums: Mapped[list["Album"]] = relationship(
        back_populates="genre", cascade="all, delete-orphan"
    )


class Album(Base):
    __tablename__ = "album"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genre.id"), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    genre: Mapped["Genre"] = relationship(back_populates="albums")
    songs: Mapped[list["Song"]] = relationship(
        back_populates="album", cascade="all, delete-orphan"
    )


class Song(Base):
    __tablename__ = "song"
    __table_args__ = (
        CheckConstraint("duration >= 0", name="ck_song_duration_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    album_id: Mapped[int] = mapped_column(ForeignKey("album.id"), index=True)
    name: Mapped[str] = mapped_column(String(200), index=True)
    duration: Mapped[int] = mapped_column()
    status: Mapped[SongStatus] = mapped_column(
        SAEnum(SongStatus, name="song_status"), default=SongStatus.DRAFT, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    album: Mapped["Album"] = relationship(back_populates="songs")
