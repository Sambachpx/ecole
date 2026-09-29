from sqlalchemy import select
from sqlalchemy.orm import Session

from ecole.models import Album, Genre, Song, Status


def is_empty(db: Session) -> bool:
    return db.scalar(select(Genre.id).limit(1)) is None


def seed(db: Session) -> None:
    rock = Genre(name="Rock")
    jazz = Genre(name="Jazz")
    db.add_all([rock, jazz])
    db.flush()  # assign genre ids

    abbey_road = Album(name="Abbey Road", genre_id=rock.id)
    kind_of_blue = Album(name="Kind of Blue", genre_id=jazz.id)
    db.add_all([abbey_road, kind_of_blue])
    db.flush()  # assign album ids

    db.add_all(
        [
            Song(
                name="Come Together",
                duration=259,
                album_id=abbey_road.id,
                status=Status.PUBLISHED,
            ),
            Song(
                name="Something",
                duration=182,
                album_id=abbey_road.id,
                status=Status.PUBLISHED,
            ),
            Song(
                name="So What",
                duration=562,
                album_id=kind_of_blue.id,
                status=Status.PUBLISHED,
            ),
            Song(name="Blue in Green", duration=337, album_id=kind_of_blue.id),
        ]
    )
    db.commit()
