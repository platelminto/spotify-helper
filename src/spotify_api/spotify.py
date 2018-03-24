import datetime
import platform

from main.notif_handler import send_notif
from spotify_api.web_api import WebApi
from spotify_api.dbus_api import get_track_id


class Spotify:

    def __init__(self):

        self.current_os = platform.system()

        keys_file = open('../keys.txt')

        client_id = keys_file.readline().rstrip()
        client_secret = keys_file.readline().rstrip()

        keys_file.close()

        redirect_uri = 'http://localhost:8888/callback'

        scope_list = ['user-library-read', 'user-library-modify', 'user-read-currently-playing',
                      'playlist-modify-public']

        self.api = WebApi(scope_list=scope_list, client_id=client_id,
                          client_secret=client_secret, redirect_uri=redirect_uri)

    def fetch_user_id(self):
        return self.api.get('me').json().get('id')

    def monthly_playlist_id(self):
        now = datetime.datetime.now()
        month, year = now.strftime('%B'), str(now.year)
        try:
            file = open('../month_id.txt', 'r')

            if file.readline().rstrip() == month + year:

                playlist_id = file.readline()

                if playlist_id != '':
                    return playlist_id

            file.close()

            raise ValueError

        except (FileNotFoundError, ValueError):

            file = open('../month_id.txt', 'w+')

            file.write(month + year + '\n')
            file.write(self.fetch_playlist_id(month, year))

            file.close()

            return self.monthly_playlist_id()

    def get_user_id(self):
        try:
            with open('../user_id.txt', 'r') as user_id:
                line = user_id.readline()
                if line == '':
                    raise FileNotFoundError
                return line
        except FileNotFoundError:

            with open('../user_id.txt', 'w+') as user_id:
                user_id.write(self.fetch_user_id())

            return self.get_user_id()

    def fetch_playlist_id(self, month, year):
        response = self.api.get('me/playlists', params={'limit': '10'}).json()

        for playlist in response.get('items'):

            if str(playlist.get('name')).lower() == (month + ' ' + year).lower():
                return playlist.get('id')

        return self.api.post('users/' + self.get_user_id() + '/playlists',
                             payload={'name': (month.capitalize() + ' ' + year)}).json().get('id')

    def add_songs_to_monthly_playlist(self, *song_ids):
        return self.api.post('users/' + self.get_user_id() + '/playlists/' + self.monthly_playlist_id() + '/tracks',
                             payload={'uris': song_ids})

    def remove_song_from_monthly_playlist(self, song_id):
        return self.api.delete('users/' + self.get_user_id() + '/playlists/' + self.monthly_playlist_id() + '/tracks',
                               payload={'tracks': [{'uri': song_id}]})

    def add_songs_to_library(self, *song_ids):
        return self.api.put('me/tracks', data={'ids': song_ids})

    def currently_playing_id(self):
        try:

            return get_track_id()

        except ModuleNotFoundError:
            try:
                response = self.api.get('me/player/currently-playing')
                
                if response.status_code == 204:
                    send_notif('Error', 'No song currently playing')
                else:
                    return response.json().get('item').get('id')
            except AttributeError:
                send_notif('Error', '')
                return None

    def is_saved(self, song_id):
        return self.api.get('me/tracks/contains?ids=' + song_id).json()[0]

    def remove_songs_from_library(self, *song_ids):
        return self.api.delete('me/tracks', payload={'ids': song_ids})
