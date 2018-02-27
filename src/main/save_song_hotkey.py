import os
import sys
import platform

from pynput.keyboard import Key, Listener

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
current_os = platform.system()

import spotify_api.spotify as spotify

if current_os == 'Linux':

    import notify2

notif_icon_path = os.path.abspath('../resources/spotify.png')
notif_duration_ms = 3100


def apple_notify(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))


def linux_notify(title, text, icon_path, duration):

    notify2.init('')

    n = notify2.Notification(title, text, icon=icon_path)

    n.set_timeout(duration)
    n.show()


def save_song():
    song_id = spotify.currently_playing_id()

    is_saved = spotify.is_saved(song_id)

    if is_saved:

        make_notif(spotify.remove_songs_from_library(song_id), 'removed from', 'remove from')

    else:

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


def on_press(key):
    if key == Key.f8:
        save_song()


with Listener(on_press=on_press) as listener:
    listener.join()
