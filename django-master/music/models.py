from django.db import models

# Create your models here.
class Song(models.Model):
    name = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    release_year = models.IntegerField()

class Playlist(models.Model):
    name = models.CharField(max_length=100,default='UndefinedPlaylist')

    def __str__(self):
        return self.name

class PlaylistSong(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    position = models.PositiveIntegerField()

    class Meta:
        unique_together = ('playlist', 'position')  # Ensure unique position within a playlist

    def __str__(self):
        return f"{self.playlist.name} - {self.song.name} (Position: {self.position})"

class models(models.Model):
    PlaylistSong = models.CharField(max_length=100,default='UndefinedPlaylist')

    def __str__(self):
        return self.name