import datetime
import platform

from main.notif_handler import send_notif, send_notif_with_web_image
from spotify_api.applescript_api import AppleScriptApi
from spotify_api.dbus_api import DBusApi
from spotify_api.web_api import WebApi


def get_device_name():

    return platform.uname()[1]


class Spotify:

    def __init__(self):

        self.current_os = platform.system()

        keys_file = open('../keys.txt')

        client_id = keys_file.readline().rstrip()
        client_secret = keys_file.readline().rstrip()

        keys_file.close()

        redirect_uri = 'http://localhost:8888/callback'

        scope_list = ['user-library-read', 'user-library-modify', 'playlist-modify-public',
                      'user-modify-playback-state', 'user-read-playback-state']

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
        return self.web_api.put('me/tracks', payload={'ids': song_ids})

    def available_devices(self):

        return self.web_api.get('me/player/devices').json().get('devices')

    def current_device(self):

        devices = self.available_devices()
        return next(device for device in devices if device.get('is_active'))

    def show_current_song(self):

        def get_track_from_web_api(response):

            response.json().get('item')

        track = self.try_local_method_then_web('get_current_track', '', 'get', get_track_from_web_api)

        song = track.get('name')
        artists = [x.get('name') for x in track.get('artists')]
        album = track.get('album').get('name')

        send_notif_with_web_image(song, ', '.join(artists) + ' - ' + album, self.currently_playing_art_url())

    def currently_playing_id(self):

        def get_id_from_web_api(response):
            return response.json().get('item').get('id')

        return self.try_local_method_then_web('get_track_id', '', 'get', get_id_from_web_api, 'get')

    def is_saved(self, song_id):

        return self.web_api.get('me/tracks/contains?ids=' + song_id).json()[0]

    def currently_playing_art_url(self, track=None, quality=2):

        if track is None:
            try:
                track = self.try_local_method_then_web('', '', 'get').json().get('item')

            except ConnectionError:

                return None

        images = track.get('album').get('images')

        return images[-quality if len(images) >= 2 else 0].get('url')

    def remove_songs_from_library(self, *song_ids):

        return self.web_api.delete('me/tracks', payload={'ids': song_ids})

    def is_playing(self):

        return self.try_local_method_then_web('is_playing', '', 'get').json().get('is_playing')

    def get_shuffle_and_repeat_state(self):

        response = self.web_api.get('me/player').json()

        return response.get('shuffle_state'), response.get('repeat_state')

    def next(self):

        self.try_local_method_then_web('next', 'next', 'post')

    def previous(self):

        self.try_local_method_then_web('previous', 'previous', 'post')

    def restart(self):

        self.try_local_method_then_web('restart', 'seek', 'put', params={'position_ms': 0})

    def pause(self):

        self.try_local_method_then_web('pause', 'pause', 'put')

    def toggle_play(self):

        try:

            self.local_api.play_pause()

        except AttributeError:

            is_playing = self.is_playing()

            if is_playing:
                self.pause()
            else:
                self.play()

    def play(self):

        # self.try_local_method_then_web('play', 'play', 'put') returns error 502

        try:

            self.local_api.play()

        except AttributeError:
            self.call_player_method('', 'put', payload={'play': True,
                                                        'device_ids': [self.current_device().get('id')]})

    def save(self):

        if not self.is_saved(self.currently_playing_id()):

            self.add_songs_to_library(self.currently_playing_id())
            send_notif('Success', 'Successfully added to library')
        else:

            send_notif('Success', 'Was already in library')

    def unsave(self):

        self.remove_songs_from_library(self.currently_playing_id())
        send_notif('Success', 'Successfully removed from library')

    def toggle_shuffle(self):

        def change_shuffle_with_web_api(response):
            toggled_shuffle = not response.json().get('shuffle_state')

            self.web_api.put('me/player/shuffle', params={'state': toggled_shuffle})
            send_notif('Shuffle toggled', 'Shuffle now ' + ('enabled' if toggled_shuffle else 'disabled'))

        self.try_local_method_then_web('toggle_shuffle', '', 'get', change_shuffle_with_web_api)

    def toggle_repeat(self):

        def change_state_with_web_api(response):
            repeat_state = response.json().get('repeat_state')

            next_state = self.repeat_states[self.repeat_states.index(repeat_state) - 1]
            self.web_api.put('me/player/repeat', params={'state': next_state})
            send_notif('Repeat changed', 'Repeating is now set to: ' + next_state)

        self.try_local_method_then_web('toggle_shuffle', '', 'get', change_state_with_web_api, 'get')

    def get_current_device_id(self):

        return next(x.get(id) for x in self.call_player_method('devices', 'get').json().get('devices') if x.get('name') == get_device_name())

    def try_local_method_then_web(self, local_method_name, web_method_name, rest_function_name,
                                  do_with_web_result=lambda x: x, params=None, payload=None):

        try:

            return getattr(self.local_api, local_method_name)()

        except AttributeError:

            return do_with_web_result(self.call_player_method(web_method_name, rest_function_name, params, payload))

    def call_player_method(self, method, rest_function_name, params=None, payload=None):

        if rest_function_name == 'get':

            response = getattr(self.web_api, rest_function_name)('me/player/' + method, params=params)
        else:

            response = getattr(self.web_api, rest_function_name)('me/player/' + method, params=params, payload=payload)

        status_code = response.status_code

        if status_code is 403:
            send_notif('Error', 'Must be premium')
            return

        return response

    def toggle_save(self):

        is_saved = self.is_saved(self.currently_playing_id())

        if is_saved:
            self.unsave()

        else:
            self.save()

    def save_playlist(self):  # TODO

        pass


if __name__ == '__main__':
    spotify = Spotify()
