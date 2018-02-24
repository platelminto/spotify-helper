import keyboard
import notify2
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from spotify_api import spotify

if __name__ == '__main__':
    pass


def save_song():

    song_id = spotify.currently_playing_id()

    is_saved = spotify.is_saved(song_id)

    if is_saved:

        send_notif(spotify.remove_songs_from_library(song_id), 'removed from', 'remove from')

    else:

        send_notif(spotify.add_songs_to_library(song_id), 'added to', 'add to')


def send_notif(success, success_string, fail_string):
    notify2.init('')

    if success:

        n = notify2.Notification('Success', 'Successfully ' + success_string + ' library',
                                 icon=os.path.abspath('../resources/spotify.png'))

    else:

        n = notify2.Notification('Failed', 'Failed to ' + fail_string + ' library',
                                 icon=os.path.abspath('../resources/spotify.png'))

    n.set_timeout(3100)
    n.show()


keyboard.add_hotkey('f8', lambda: save_song())
keyboard.wait()
