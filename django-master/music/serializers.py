from rest_framework import serializers
from .models import Song , Playlist , PlaylistSong

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ['name', 'artist', 'release_year']
class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['id', 'name']
class PlaylistSongSerializer(serializers.ModelSerializer):
    song = SongSerializer()

    class Meta:
        model = PlaylistSong
        fields = ['id', 'song', 'position']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['song'] = SongSerializer(instance.song).data
        return representation

class CustomPlaylistSongSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='song.name')
    artist = serializers.CharField(source='song.artist')
    release_year = serializers.IntegerField(source='song.release_year')

    class Meta:
        model = PlaylistSong
        fields = ('id', 'name', 'artist', 'release_year', 'position')