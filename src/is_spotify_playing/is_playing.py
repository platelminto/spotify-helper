import zope.event
import threading
import subprocess
import platform

import src.is_spotify_playing.windows_playing as windows_playing
import src.is_spotify_playing.mac_playing as mac_playing


def run_command(command):

    result = subprocess.run(command.split(' '), stdout=subprocess.PIPE)

    if result.returncode is not 0:
        raise NameError

    return result.stdout.decode('utf-8').rstrip()

def fire_when_playing(event):




def start_listening():

    zope.event.subscribers.append(fire_when_playing)

    current_os = platform.system()

    if current_os == 'Linux':
        target = linux_playing.is_playing
    if current_os == 'Darwin':
        target = mac_playing.is_playing
    if current_os == 'Windows':
        target = windows_playing.is_playing

    t = threading.Thread(target=target)
    t.daemon = True
    t.start()
