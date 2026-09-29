from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Status(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    PRIVATE = "private"


class Genre(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class Album(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    genre_id: Mapped[int] = mapped_column(ForeignKey("genre.id"))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )


class Song(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    album_id: Mapped[int] = mapped_column(ForeignKey("album.id"))
    name: Mapped[str]
    duration: Mapped[int]
    status: Mapped[Status] = mapped_column(
        SAEnum(
            Status,
            create_constraint=True,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=Status.DRAFT,
    )
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
