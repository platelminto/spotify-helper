import zope.event
import time
import subprocess


def run_command(command):

    result = subprocess.run(['osascript', '-e', command], stdout=subprocess.PIPE)

    if result.returncode is not 0:
        print('Error, spotify probably not running')

    return result.stdout.decode('utf-8').rstrip()


def is_now_playing(interval):

    old_state = get_player_state()
    old_song = get_song_id()

    while True:
        state, song = get_player_state(), get_song_id()
        # if old_state != state:
        #     old_state = state
        #
        #     if state == 'playing':
        #         zope.event.notify('playing')

        if old_song != song:
            old_song = song
            if state == 'playing':
                zope.event.notify('playing')

        time.sleep(interval)


def get_player_state():

    return run_command('tell application "Spotify" to player state as string')


def get_song_id():

    return run_command('tell application "Spotify" to id of current track as string')
