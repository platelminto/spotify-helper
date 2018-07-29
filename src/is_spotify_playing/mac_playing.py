from src.is_spotify_playing.is_playing import run_command
import zope.event
import time


def is_playing(interval):

    old_state = get_player_state()

    while True:
        if old_state != get_player_state():
            old_state = get_player_state()

            if old_state == 'playing':
                zope.event.notify('playing')

        time.sleep(interval)


def get_player_state():

    return run_command('tell application "Spotify" to player state as string')