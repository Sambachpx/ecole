from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.filters import StaticValuesFilter
from sqlalchemy.engine import Engine

from ecole.models import Album, Genre, Song, Status


class GenreAdmin(ModelView, model=Genre):
    column_list = [Genre.id, Genre.name]
    column_searchable_list = [Genre.name]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    name = "Genre"
    name_plural = "Genres"
    icon = "fa-solid fa-music"


class AlbumAdmin(ModelView, model=Album):
    column_list = [Album.id, Album.name, Album.genre, Album.updated_at]
    column_searchable_list = [Album.name]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    name = "Album"
    name_plural = "Albums"
    icon = "fa-solid fa-compact-disc"


class SongAdmin(ModelView, model=Song):
    column_list = [
        Song.id,
        Song.album,
        Song.name,
        Song.duration,
        Song.status,
        Song.created_at,
    ]
    column_searchable_list = [Song.name]
    column_filters = [
        StaticValuesFilter(
            Song.status,
            values=[(s.value, s.value) for s in Status],
            title="Status",
        )
    ]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    name = "Song"
    name_plural = "Songs"
    icon = "fa-solid fa-headphones"


def setup_admin(app: FastAPI, engine: Engine) -> Admin:
    """Enregistre tous les modèles dans l'admin SQLAdmin."""
    admin = Admin(app, engine)
    admin.add_view(GenreAdmin)
    admin.add_view(AlbumAdmin)
    admin.add_view(SongAdmin)
    return admin
