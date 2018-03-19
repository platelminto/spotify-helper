import os
import sys
import platform

from pynput.keyboard import Key, Listener, KeyCode

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
current_os = platform.system()

import spotify_api.spotify as spotify
import main.windows_notif as windows_notif

if current_os == 'Linux':

    import dbus

if current_os == 'Windows':

    import threading

options_file = '../options.txt'

notif_icon_path = os.path.abspath('../resources/spotify.ico')
notif_duration_ms = 3100


def read_option(option):

    with open(options_file) as file:

        line = file.readline().rstrip()
        while not line.startswith(option):
            line = file.readline().rstrip()

        return line.split('=')[1]


monthly_playlist = read_option('monthly_playlist')

if monthly_playlist == 'yes':
    monthly_playlist = True
else:
    monthly_playlist = False


def windows_notify(title, text, icon_path, duration):
    t = threading.Thread(target=windows_notif.balloon_tip, args =
                         (title, text, icon_path, duration))
    t.daemon = True
    t.start()


def apple_notify(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))


def linux_notify(title, text, icon_path, duration):

    bus = dbus.SessionBus()

    notify = bus.get_object('org.freedesktop.Notifications', '/org/freedesktop/Notifications')
    method = notify.get_dbus_method('Notify', 'org.freedesktop.Notifications')

    method("save-song-spotify", 24, icon_path, title, text, [], [], duration)


def save_song():
    song_id = spotify.currently_playing_id()

    is_saved = spotify.is_saved(song_id)

    if is_saved:

        if monthly_playlist:
            spotify.remove_song_from_monthly_playlist('spotify:track:' + song_id)
        make_notif(spotify.remove_songs_from_library(song_id), 'removed from', 'remove from')

    else:

        if monthly_playlist:
            spotify.add_songs_to_monthly_playlist('spotify:track:' + song_id)
        make_notif(spotify.add_songs_to_library(song_id), 'added to', 'add to')


def make_notif(success, success_string, fail_string):

    full_success_string = 'Successfully ' + success_string + ' library'
    full_fail_string = 'Failed to ' + fail_string + ' library'

    if success:

        send_notif('Success', full_success_string)

    else:

        send_notif('Failure', full_fail_string)


def send_notif(title, text):

    if current_os == 'Linux':

        linux_notify(title, text, notif_icon_path, notif_duration_ms)

    elif current_os == 'Darwin':

        apple_notify(title, text)

    elif current_os == 'Windows':

        windows_notify(title, text, notif_icon_path, notif_duration_ms)


class Keyboard(object):

    @staticmethod
    def get_key_from_string(key_str):

        try:
            return getattr(Key, key_str)
        except AttributeError:
            return KeyCode.from_char(key_str)

    @staticmethod
    def is_not_char(key):
        return isinstance(key, Key)

    def __init__(self):
        self.currently_pressed_keys = set()

        self.looking_for = set()

        for key_str in read_option('key_combo').split('+'):
            self.looking_for.add(self.get_key_from_string(key_str))

    def on_press(self, key):
        self.currently_pressed_keys.add(key)

        if self.looking_for == self.currently_pressed_keys:
            save_song()
            self.currently_pressed_keys.clear()

    def on_release(self, key):
        try:
            self.currently_pressed_keys.remove(key)
        except KeyError:
            pass


keyboard = Keyboard()

with Listener(on_press=keyboard.on_press, on_release=keyboard.on_release) as listener:
    listener.join()
