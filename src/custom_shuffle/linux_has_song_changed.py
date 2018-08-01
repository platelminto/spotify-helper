import zope.event
import time
import subprocess

from spotify_api.dbus_api import DBusApi


stop = False


def run_command(command):

    result = subprocess.run(command.split(' '), stdout=subprocess.PIPE)

    if result.returncode is not 0:
        print('error')

    return result.stdout.decode('utf-8').rstrip()


def has_song_changed(interval):

    # old_state = get_player_state()
    old_song = get_song_id()

    global stop
    stop = False

    while not stop:
        state, song = get_player_state(), get_song_id()
        # if old_state != state:
        #     old_state = state
        #
        #     if state == 'RUNNING':
        #         zope.event.notify('playing')

        if old_song != song:
            old_song = song
            if state == 'RUNNING':
                zope.event.notify(get_song_id())

        time.sleep(interval)


def stop_listening():

    global stop
    stop = True


def get_song_id():

    try:

        return DBusApi().get_track_id()

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

        return state  # 'RUNNING' when playing and 'CORKED' otherwise (mostly)

    except (ValueError, UnboundLocalError):
        return ''
