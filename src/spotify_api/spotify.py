import datetime
import platform

import uuid
from main.notif_handler import send_notif, send_notif_with_web_image
from spotify_api.web_api import WebApi

current_os = platform.system()

if current_os == 'Darwin':
    from spotify_api.applescript_api import AppleScriptApi

elif current_os == 'Linux':
    from spotify_api.dbus_api import DBusApi


def get_device_name():
    return platform.uname()[1]


class Spotify:

    def __init__(self):
        keys_file = open('../keys.txt')
        client_id = keys_file.readline().rstrip()
        keys_file.close()

        try:
            with open('../uuid.txt') as uuid_file:
                self.uuid = uuid.UUID(uuid_file.readline().rstrip())

        except (FileNotFoundError, ValueError):
            with open('../uuid.txt', 'w') as uuid_file:
                new_uuid = uuid.uuid4()
                uuid_file.write(str(new_uuid))
                self.uuid = new_uuid

        redirect_uri = 'https://platelminto.eu.pythonanywhere.com/users/registering'

        scope_list = ['user-library-read', 'user-library-modify', 'playlist-modify-public',
                      'user-modify-playback-state', 'user-read-playback-state']

        self.web_api = WebApi(scope_list=scope_list, client_id=client_id,
                              redirect_uri=redirect_uri, uuid=self.uuid)
        if current_os == 'Darwin':
            self.local_api = AppleScriptApi()

        elif current_os == 'Linux':
            self.local_api = DBusApi()

        self.repeat_states = ['track', 'context', 'off']

    def __fetch_user_id(self):
        return self.web_api.get('me').json().get('id')

    def get_monthly_playlist_id(self):
        now = datetime.datetime.now()
        month, year = now.strftime('%B'), str(now.year)

        try:
            with open('../month_id.txt') as file:
                line = file.readline().rstrip()

                if line == month + year:
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
        response = self.web_api.get('me/playlists').json()

        for playlist in response.get('items'):
            if str(playlist.get('name')).lower() == (month + ' ' + year).lower():
                return playlist.get('id')

        return self.web_api.post('users/' + self.get_user_id() + '/playlists',
                                 payload={'name': (month.capitalize() + ' ' + year)}).json().get('id')

    def add_song_to_monthly_playlist(self, song_id):
        return self.web_api.post(
            'users/' + self.get_user_id() + '/playlists/' + self.get_monthly_playlist_id() + '/tracks',
            params={'uris': 'spotify:track:' + song_id})

    def remove_song_from_monthly_playlist(self, song_id):
        return self.web_api.delete(
            'users/' + self.get_user_id() + '/playlists/' + self.get_monthly_playlist_id() + '/tracks',
            payload={'tracks': [{'uri': 'spotify:track:' + song_id}]})

    def toggle_save_monthly_playlist(self):
        song_id = self.get_current_song_id()
        is_in_playlist = self.is_in_playlist(song_id)

        song = self.get_current_song_info()[0]

        if is_in_playlist:
            self.remove_song_from_monthly_playlist(song_id)
            send_notif_with_web_image('Successfully removed',
                                      'Removed ' + song + ' from playlist.',
                                      self.currently_playing_art_url())
        else:
            self.add_song_to_monthly_playlist(song_id)
            send_notif_with_web_image('Successfully added',
                                      'Added ' + song + ' to playlist.',
                                      self.currently_playing_art_url())

    def is_in_playlist(self, song_id):
        playlist_tracks = self.web_api.get('users/' + self.get_user_id() +
                                           '/playlists/' + self.get_monthly_playlist_id() +
                                           '/tracks').json().get('items')

        return len([x for x in playlist_tracks if x.get('track').get('id') == song_id]) > 0

    def add_songs_to_library(self, *song_ids):
        return self.web_api.put('me/tracks', payload={'ids': song_ids})

    def get_available_devices(self):
        return self.web_api.get('me/player/devices').json().get('devices')

    # The active device is the one currently playing music, not necessarily the one currently
    # being used by the user (for example, music could be playing through a phone, but the user
    # is on their computer).
    def get_active_device(self):
        devices = self.get_available_devices()
        try:
            return next(device for device in devices if device.get('is_active'))

        except StopIteration:
            return None

    def show_current_song(self):
        song, artists, album = self.get_current_song_info()
        send_notif_with_web_image(song, ', '.join(artists) + ' - ' + album, self.currently_playing_art_url())

    def get_current_song_info(self):
        def get_track_from_web_api(response):
            return response.json().get('item')

        track = self.try_local_method_then_web('get_current_track', '', 'get', get_track_from_web_api)

        song = track.get('name')
        artists = [x.get('name') for x in track.get('artists')]
        album = track.get('album').get('name')

        return song, artists, album

    def get_current_song_id(self):
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

        # We don't need very high quality images for notifications, so we get
        # the images at the end of the list (which is ordered by quality).
        return images[-quality if len(images) >= 2 else 0].get('url')

    def remove_songs_from_library(self, *song_ids):
        return self.web_api.delete('me/tracks', payload={'ids': song_ids})

    def is_playing(self):
        return self.try_local_method_then_web('is_playing', '', 'get').json().get('is_playing')

    # Utility method for possible future use.
    def get_shuffle_and_repeat_state(self):
        response = self.web_api.get('me/player').json()
        return response.get('shuffle_state'), response.get('repeat_state')

    def next(self):
        self.try_local_method_then_web('next', 'next', 'post')

    def previous(self):
        self.try_local_method_then_web('previous', 'previous', 'post')

    # Starting a song over means setting its current playing-time to 0.
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
        # Web API method for 'play' is currently broken, so instead we use the 'transfer playback'
        # endpoint to "transfer" playback to the already active device, which allows us to give it
        # a 'play' parameter to resume playback. This is done in call_play_method() to ensure
        # an API call is made only if a local API isn't available.
        self.try_local_method_then_web('play', '', 'put')

    # This does not toggle save, so if a song is already saved it doesn't remove it.
    def save(self):
        song = self.get_current_song_info()[0]

        if not self.is_saved(self.get_current_song_id()):
            self.add_songs_to_library(self.get_current_song_id())
            send_notif_with_web_image('Successfully saved',
                                      'Added ' + song + ' to library.',
                                      self.currently_playing_art_url())
        else:
            send_notif_with_web_image('Already saved',
                                      song + ' was already in library.',
                                      self.currently_playing_art_url())

    # This also doesn't toggle, so unsaving a song that isn't saved just does nothing.
    def unsave(self):
        song = self.get_current_song_info()[0]

        self.remove_songs_from_library(self.get_current_song_id())
        send_notif_with_web_image('Successfully unsaved',
                                  'Removed ' + song + ' from library.',
                                  self.currently_playing_art_url())

    def toggle_shuffle(self):
        def change_shuffle_with_web_api(response):
            toggled_shuffle = not response.json().get('shuffle_state')

            self.web_api.put('me/player/shuffle', params={'state': toggled_shuffle})
            send_notif('Shuffle toggled', 'Shuffle now ' + ('enabled' if toggled_shuffle else 'disabled'))

        self.try_local_method_then_web('toggle_shuffle', '', 'get', change_shuffle_with_web_api)

    def toggle_repeat(self):
        # There are 3 repeat states (off, track, context), so we cannot simply toggle
        # on and off, we must switch between them.
        def change_state_with_web_api(response):
            repeat_state = response.json().get('repeat_state')

            next_state = self.repeat_states[self.repeat_states.index(repeat_state) - 1]
            self.web_api.put('me/player/repeat', params={'state': next_state})
            send_notif('Repeat changed', 'Repeating is now set to: ' + next_state)

        self.try_local_method_then_web('toggle_repeat', '', 'get', change_state_with_web_api, 'get')

    def play_on_current_device(self):
        self.call_player_method('', 'put', payload={'device_ids': [self.get_current_device_id()]})

    def get_current_device_id(self):
        return next(x.get('id') for x in self.call_player_method('devices', 'get').json().get('devices') if
                    x.get('name') == get_device_name())

    # For every method, we first try a local API, and then move onto the Web API as a fallback.
    def try_local_method_then_web(self, local_method_name, web_method_name, rest_function_name,
                                  do_with_web_result=lambda x: x, params=None, payload=None):
        try:
            return getattr(self.local_api, local_method_name)()

        except AttributeError:
            return do_with_web_result(
                self.call_player_method(web_method_name, rest_function_name, params=params, payload=payload))

    def call_player_method(self, method, rest_function_name, params=None, payload=None):
        # 'get' functions don't have payloads.
        if rest_function_name == 'get':
            response = getattr(self.web_api, rest_function_name)('me/player/' + method, params=params)
        # get_active_devices() is here to avoid unnecessarily calls if not using the Web API.
        elif method == '' and rest_function_name == 'put':
            response = getattr(self.web_api, rest_function_name)('me/player/' + method, params=params,
                                                                 payload={
                                                                     'device_ids': [self.get_active_device().get('id')],
                                                                     'play': True})
        else:
            response = getattr(self.web_api, rest_function_name)('me/player/' + method, params=params, payload=payload)

        status_code = response.status_code

        if status_code is 403:
            send_notif('Error', 'Must be premium')
            return

        # 'get' with no further method returns information about the user's playback.
        # 204s are usually successes, but in this case it means no active devices exist.
        if status_code is 204 and method == '' and rest_function_name == 'get':
            send_notif('Error', 'No device found')
            return

        return response

    def toggle_save(self):
        is_saved = self.is_saved(self.get_current_song_id())

        if is_saved:
            self.unsave()
        else:
            self.save()


if __name__ == '__main__':
    spotify = Spotify()
