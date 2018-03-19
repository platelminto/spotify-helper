from pynput.keyboard import Listener

import spotify_api.spotify as spotify
from main import keyboard_handler, notif_handler

options_file = '../options.txt'


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


def save_song():
    song_id = spotify.currently_playing_id()

    is_saved = spotify.is_saved(song_id)

    if is_saved:

        if monthly_playlist:
            spotify.remove_song_from_monthly_playlist('spotify:track:' + song_id)
        notif_handler.make_notif(spotify.remove_songs_from_library(song_id), 'removed from', 'remove from')

    else:

        if monthly_playlist:
            spotify.add_songs_to_monthly_playlist('spotify:track:' + song_id)
        notif_handler.make_notif(spotify.add_songs_to_library(song_id), 'added to', 'add to')


keyboard = keyboard_handler.KeyboardHandler()

with Listener(on_press=keyboard.on_press, on_release=keyboard.on_release) as listener:
    listener.join()
