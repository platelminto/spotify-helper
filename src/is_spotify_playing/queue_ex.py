import zope.event
import threading
import time
import os
from pathlib import Path


def fire_when_playing(event):
    if event == 'playing':
        print('playing')
    else:
        print('nope')


def find_state():

    now_playing_file = get_now_playing_file()
    last_modif_time = last_modified(now_playing_file)

    while True:

        if last_modif_time == last_modified(now_playing_file):
            pass

        else:
            zope.event.notify('playing')
            last_modif_time = last_modified(now_playing_file)

        time.sleep(5)


def get_now_playing_file():

    spotify_dir = get_spotify_dir()

    for item in os.listdir(spotify_dir):
        if 'ad-state-storage.bnk' in item:
            now_playing_file = item

    return spotify_dir + '/' + now_playing_file


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

    return str(Path(spotify_dir))  # String brackets are broken so passing it through Path() fixes it


def last_modified(path):

    return os.path.getmtime(path)


zope.event.subscribers.append(fire_when_playing)

t = threading.Thread(target=find_state)
t.daemon = False
t.start()
