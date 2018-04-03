import datetime
import platform

from main.notif_handler import send_notif
from spotify_api.applescript_api import AppleScriptApi
from spotify_api.dbus_api import DBusApi
from spotify_api.web_api import WebApi


class Spotify:

    def __init__(self):

        self.current_os = platform.system()

        keys_file = open('../keys.txt')

        client_id = keys_file.readline().rstrip()
        client_secret = keys_file.readline().rstrip()

        keys_file.close()

        redirect_uri = 'http://localhost:8888/callback'

        scope_list = ['user-library-read', 'user-library-modify', 'user-read-currently-playing',
                      'playlist-modify-public', 'user-modify-playback-state']

        self.web_api = WebApi(scope_list=scope_list, client_id=client_id,
                              client_secret=client_secret, redirect_uri=redirect_uri)
        if self.current_os == 'Darwin':
            self.local_api = AppleScriptApi()

        elif self.current_os == 'Linux':
            self.local_api = DBusApi()

        self.repeat_states = ['track', 'context', 'off']

    def __fetch_user_id(self):
        return self.web_api.get('me').json().get('id')

    def get_monthly_playlist_id(self):
        now = datetime.datetime.now()
        month, year = now.strftime('%B'), str(now.year)

        try:
            with open('../month_id.txt', 'r') as file:

                if file.readline().rstrip() == month + year:

                    playlist_id = file.readline()

                    if playlist_id != '':
                        return playlist_id

                raise ValueError

        except (FileNotFoundError, ValueError):

            with open('../month_id.txt', 'w+') as file:

                file.write(month + year + '\n')
                file.write(self.__fetch_playlist_id(month, year))

                return self.get_monthly_playlist_id()

    def get_user_id(self):
        try:
            with open('../user_id.txt', 'r') as user_id:
                line = user_id.readline()
                if line == '':
                    raise FileNotFoundError
                return line
        except FileNotFoundError:

            with open('../user_id.txt', 'w+') as user_id:
                user_id.write(self.__fetch_user_id())

            return self.get_user_id()

    def __fetch_playlist_id(self, month, year):
        response = self.web_api.get('me/playlists', params={'limit': '10'}).json()

        for playlist in response.get('items'):

            if str(playlist.get('name')).lower() == (month + ' ' + year).lower():
                return playlist.get('id')

        return self.web_api.post('users/' + self.get_user_id() + '/playlists',
                                 payload={'name': (month.capitalize() + ' ' + year)}).json().get('id')

    def add_songs_to_monthly_playlist(self, *song_ids):
        return self.web_api.post('users/' + self.get_user_id() + '/playlists/' + self.get_monthly_playlist_id() + '/tracks',
                                 payload={'uris': song_ids})

    def remove_song_from_monthly_playlist(self, song_id):
        return self.web_api.delete('users/' + self.get_user_id() + '/playlists/' + self.get_monthly_playlist_id() + '/tracks',
                                   payload={'tracks': [{'uri': song_id}]})

    def add_songs_to_library(self, *song_ids):
        return self.web_api.put('me/tracks', data={'ids': song_ids})

    def currently_playing_id(self):
        try:

            return self.local_api.get_track_id()

        except AttributeError:
            try:
                response = self.web_api.get('me/player/currently-playing')
                
                if response.status_code == 204:
                    send_notif('Error', 'No song currently playing')
                else:
                    return response.json().get('item').get('id')
            except AttributeError:
                return send_generic_error()

    def is_saved(self, song_id):

        return self.web_api.get('me/tracks/contains?ids=' + song_id).json()[0]

    def remove_songs_from_library(self, *song_ids):

        return self.web_api.delete('me/tracks', payload={'ids': song_ids})

    def is_playing(self):

        response = self.web_api.get('me/player/currently-playing')
        status_code = response.status_code

        if status_code == 204 or 200:

            return False

        return response.json().get('is_playing') == 'true'

    def get_shuffle_and_repeat_state(self):

        response = self.web_api.get('me/player').json()

        return response.get('shuffle_state') == 'true', response.get('repeat_state')

    def next(self):

        return self.try_local_method_then_web('next', 'next')

    def previous(self):

        return self.try_local_method_then_web('previous', 'previous')

    def pause(self):

        return self.try_local_method_then_web('pause', 'pause')

    def toggle_play(self):

        is_playing = self.is_playing()

        if is_playing:
            return self.pause()

        return self.play()

    def play(self):

        return self.try_local_method_then_web('play', 'play')

    def toggle_shuffle(self):  # TODO: add support for local api (applescript), add notif

        is_shuffled = self.get_shuffle_and_repeat_state()[0]

        return self.web_api.put('me/player/shuffle', data={'state': not is_shuffled})

    def toggle_repeat(self):  # TODO: add support for local api (applescript), add notif

        repeat_state = self.get_shuffle_and_repeat_state()[1]
        next_state = self.repeat_states[self.repeat_states.index(repeat_state)-1]

        return self.web_api.put('me/player/repeat', data={'state': next_state})

    def try_local_method_then_web(self, local_method_name, web_method_name):

        try:

            return getattr(self.local_api, local_method_name)()

        except AttributeError:

            self.call_player_method(web_method_name)

    def call_player_method(self, method):

        response = self.web_api.post('me/player/' + method)
        status_code = response.status_code

        if status_code is 403:

            send_notif('Error', 'Must be premium')

        elif status_code is not 204:

            return send_generic_error()

    def save(self):

        song_id = self.currently_playing_id()

        if song_id:
            is_saved = self.is_saved(song_id)

            if is_saved:
                self.remove_songs_from_library(song_id)
                send_notif('Success', 'Successfully removed from library')

            else:
                self.add_songs_to_library(song_id)
                send_notif('Success', 'Successfully added to library')

    def save_playlist(self):

        pass

def send_generic_error():

    return send_notif('Error', '')
