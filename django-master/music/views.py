from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from .models import Song , PlaylistSong , Playlist , models
from .serializers import SongSerializer ,  PlaylistSerializer ,  PlaylistSongSerializer , CustomPlaylistSongSerializer
from rest_framework import status

# Create your views here.
from django.http import HttpResponse

# This is create and list all the songs in the db with the pagination
@api_view(['GET', 'POST'])
def songs(request):
    if request.method == 'POST':
        try:
            existing_song = Song.objects.filter(name=request.data.get('name')).first()
            if existing_song:
                return Response({
                    "message": "Error. This song already exists."
                }, status=status.HTTP_409_CONFLICT)

            serializer = SongSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Success. The song entry has been created."
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        paginator = PageNumberPagination()
        paginator.page_size = 10 

        song_name = request.query_params.get('q')
        songs_query = Song.objects.all().order_by('id')
        if song_name:
            songs_query = songs_query.filter(name__icontains=song_name)

        result_page = paginator.paginate_queryset(songs_query, request)
        serializer = SongSerializer(result_page, many=True)
        
        return paginator.get_paginated_response(serializer.data)

        
# This is Create and list playlist route .
@api_view(['GET', 'POST'])
def create_playlist(request):
    if request.method == 'POST':
        try:
            # Extract data from request body
            name = request.data.get('name')
            songs = request.data.get('songs')

            # Validate request data
            if not name or not songs:
                return Response({'message': 'Name and songs are required.'}, status=status.HTTP_400_BAD_REQUEST)

            # Create playlist
            playlist = Playlist.objects.create(name=name)

            # Add songs to playlist with their positions
            for position, song_id in enumerate(songs, start=1):
                song = Song.objects.get(pk=song_id)
                data = PlaylistSong.objects.create(playlist=playlist, song=song, position=position)
                print(data)

            return Response({'message': 'Success. The playlist entry has been created.'}, status=status.HTTP_201_CREATED)
        except Song.DoesNotExist:
            return Response({'message': 'One or more songs do not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        page_number = request.query_params.get('page', 1)
        search_query = request.query_params.get('q', '')

        # Filter playlists based on search query
        playlists_query = Playlist.objects.all().order_by('id')
        if search_query:
            playlists_query = playlists_query.filter(name__icontains=search_query)

        # Paginate the queryset
        paginator = PageNumberPagination()
        paginator.page_size = 10
        playlists_page = paginator.paginate_queryset(playlists_query, request)

        # Serialize paginated playlists
        serializer = PlaylistSerializer(playlists_page, many=True)

        # Construct the response data
        response_data = {
            'count': playlists_query.count(),  # Total count ignoring pagination
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'results': serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)

    
#5 - Edit playlist metadata
@api_view(['PUT','DELETE'])
def edit_playlist(request, playlist_id):
    if request.method == 'PUT':
        try:
            playlist = Playlist.objects.get(id=playlist_id)
        except Playlist.DoesNotExist:
            return Response({'message': 'Playlist not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PlaylistSerializer(playlist, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Success. The playlist name has been edited."
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
        # Retrieve playlist object from database
            playlist = Playlist.objects.get(pk=playlist_id)

            # Delete playlist
            playlist.delete()

            return Response({'message': 'Success. The playlist has been deleted.'}, status=status.HTTP_200_OK)
        except Playlist.DoesNotExist:
            return Response({'message': 'Playlist not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#7 List playlist songs
@api_view(['GET'])
def list_playlist_songs(request, playlist_id):
    try:
        # Retrieve playlist songs queryset and order by position
        playlist_songs_query = PlaylistSong.objects.filter(playlist_id=playlist_id).order_by('position')

        # Paginate the queryset
        paginator = PageNumberPagination()
        paginator.page_size = 10
        playlist_songs_page = paginator.paginate_queryset(playlist_songs_query, request)

        # Serialize paginated playlist songs
        serializer = CustomPlaylistSongSerializer(playlist_songs_page, many=True)

        # Construct the response data
        response_data = {
            'count': playlist_songs_query.count(),  # Total count ignoring pagination
            'next': paginator.get_next_link(),
            'previous': paginator.get_previous_link(),
            'results': serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


#8 Move playlist song
@api_view(['PUT','DELETE'])
def move_playlist_song(request, playlist_id, song_id):
    if request.method == 'PUT':
        try:
            # Retrieve playlist song object from the database
            playlist_song = PlaylistSong.objects.get(playlist_id=playlist_id, song_id=song_id)
            
            # Parse request body
            new_position = request.data.get('position')
            
            # Get the current position of the song
            current_position = playlist_song.position
            
            # Update the position of the song
            playlist_song.position = new_position
            playlist_song.save()
            
            # Adjust the positions of all affected songs
            if new_position < current_position:
                # Move song up in the playlist
                PlaylistSong.objects.filter(playlist_id=playlist_id, position__gte=new_position, position__lt=current_position).exclude(song_id=song_id).update(position=models.F('position') + 1)
            elif new_position > current_position:
                # Move song down in the playlist
                PlaylistSong.objects.filter(playlist_id=playlist_id, position__gt=current_position, position__lte=new_position).exclude(song_id=song_id).update(position=models.F('position') - 1)
            
            return Response({'message': 'Success. Song has been moved to the new position in the playlist.'}, status=status.HTTP_200_OK)
        except PlaylistSong.DoesNotExist:
            return Response({'error': 'Playlist song not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            # Retrieve playlist song object from the database
            playlist_song = PlaylistSong.objects.get(playlist_id=playlist_id, song_id=song_id)
            
            # Get the position of the song being removed
            removed_position = playlist_song.position
            
            # Delete the playlist song object
            playlist_song.delete()
            
            # Adjust the positions of all subsequent songs
            PlaylistSong.objects.filter(playlist_id=playlist_id, position__gt=removed_position).update(position=models.F('position') - 1)
            
            return Response({'message': 'Success. Song has been removed from the playlist.'}, status=status.HTTP_200_OK)
        except PlaylistSong.DoesNotExist:
            return Response({'error': 'Playlist song not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    
