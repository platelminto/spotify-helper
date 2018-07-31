import zope.event
import time
import os
from pathlib import Path


stop = False


def has_song_changed(interval):

    now_playing_file = get_song_changed_file()
    last_modif_time = last_modified(now_playing_file)

    global stop
    stop = False

    while not stop:

        if last_modif_time != last_modified(now_playing_file):
            zope.event.notify('playing')
            last_modif_time = last_modified(now_playing_file)

        time.sleep(interval)


def get_song_changed_file():

    spotify_dir = get_spotify_dir()

    for item in os.listdir(spotify_dir):
        if 'recently_played.bnk' in item:
            now_playing_file = item

    return spotify_dir + '/' + now_playing_file


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
