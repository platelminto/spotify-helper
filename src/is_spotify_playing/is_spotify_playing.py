import platform
import subprocess
import time


def alert_when_spotify_playing(interval):
    current_os = platform.system()

    if current_os == 'Linux':
        return is_playing_linux(interval)
    if current_os == 'Darwin':
        return is_playing_mac(interval)
    if current_os == 'Windows':
        return is_playing_windows(interval)


def run_command(command):

    result = subprocess.run(command.split(' '), stdout=subprocess.PIPE)

    if result.returncode is not 0:
        raise NameError

    return result.stdout.decode('utf-8').rstrip()


def is_playing_mac(interval):

    state = run_command('tell application "Spotify" to player state as string')

    return state == 'paused'


def is_playing_windows():

    import os




def is_playing_linux():

    pacmd = run_command('pacmd list-sink-inputs')

    try:
        for process in pacmd.split('index: '):
            if process.find('<Spotify>') != -1:
                for line in process.split('\n'):
                    if line.strip().startswith('state'):
                        state_line = line
                        break

        state = state_line.strip().split(' ')[1]

        if state == 'RUNNING':
            return True

        return False

    except (ValueError, UnboundLocalError):
        return False

print(is_spotify_playing())
