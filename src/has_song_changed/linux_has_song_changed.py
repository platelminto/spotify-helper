import zope.event
import time
import subprocess

from spotify_api.dbus_api import DBusApi


def run_command(command):

    result = subprocess.run(command.split(' '), stdout=subprocess.PIPE)

    if result.returncode is not 0:
        print('error')

    return result.stdout.decode('utf-8').rstrip()


def is_now_playing(interval):

    old_state = get_player_state()
    old_song = get_song_id()

    while True:
        state, song = get_player_state(), get_song_id()
        # if old_state != state:
        #     old_state = state
        #
        #     if state == 'RUNNING':
        #         zope.event.notify('playing')

        if old_song != song:
            old_song = song
            if state == 'RUNNING':
                zope.event.notify('playing')

        time.sleep(interval)


def get_song_id():

    try:
        dbus_api = DBusApi()

        return dbus_api.get_track_id()

    except Exception:
        return ''


def get_player_state():

    pacmd = run_command('pacmd list-sink-inputs')

    try:
        for process in pacmd.split('index: '):
            if process.find('<Spotify>') != -1:
                for line in process.split('\n'):
                    if line.strip().startswith('state'):
                        state_line = line
                        break

        state = state_line.strip().split(' ')[1]

        return state

    except (ValueError, UnboundLocalError):
        return ''
