import zope.event
import time
import os
from pathlib import Path

SONG_ID_LENGTH = 22

stop = False


def has_song_changed(interval):

    now_playing_file = get_song_changed_file()
    last_modif_time = last_modified(now_playing_file)

    global stop
    stop = False

    while not stop:

        if last_modif_time != last_modified(now_playing_file):
            zope.event.notify(get_song_id())
            last_modif_time = last_modified(now_playing_file)

        time.sleep(interval)


def get_song_changed_file():

    spotify_dir = get_spotify_dir()

    for item in os.listdir(spotify_dir):
        if 'recently_played.bnk' in item:
            now_playing_file = item
            break

    return spotify_dir + '/' + now_playing_file


def get_song_id():

    spotify_dir = get_spotify_dir()

    for item in os.listdir(spotify_dir):
        if 'recently_played.bnk' in item:
            now_playing_file = item
            break

    with open(spotify_dir + '/' + now_playing_file) as playing_file:

        curent_song_line = playing_file.readline()
        current_song_marker = 'spotify:track:'

        while current_song_marker not in curent_song_line:
            curent_song_line = playing_file.readline()

        id_beginning_index = curent_song_line.find(current_song_marker) + len(curent_song_line)

    return curent_song_line[id_beginning_index:id_beginning_index+SONG_ID_LENGTH]


def stop_listening():

    global stop
    stop = True


def get_spotify_dir():

    spotify_dir = str(Path.home())

    spotify_dir += '/AppData/Local/Packages/'

    for item in os.listdir(spotify_dir):

        if 'Spotify' in item:

            spotify_dir += '/' + str(item)

    spotify_dir += '/LocalState/Spotify/Users'

    with open('../user_id.txt') as user_id:

        username = user_id.readline()

    spotify_dir += '/' + username + '-user'

    return str(Path(spotify_dir))  # Slashes are both / & \ so passing it through Path() fixes it up


def last_modified(path):

    return os.path.getmtime(path)
