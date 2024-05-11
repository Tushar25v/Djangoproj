from django.urls import path

from . import views

urlpatterns = [
    path("songs", views.songs, name="add songs and list all the songs"),
    path("playlists", views.create_playlist, name="create_playlist and list playlist"),
    path('playlists/<int:playlist_id>', views.edit_playlist, name='edit-playlist and delete-playlist'),
    path('playlists/<int:playlist_id>/songs', views.list_playlist_songs, name='list-playlist-songs'),
    path('playlists/<int:playlist_id>/songs/<int:song_id>', views.move_playlist_song, name='move-playlist-song')
]   