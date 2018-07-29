import zope.event
import threading
import platform
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import linux_playing, mac_playing, windows_playing


def fire_when_playing(event):

    print('wooooo')


def start_listening(interval, daemon=True):

    zope.event.subscribers.append(fire_when_playing)

    current_os = platform.system()

    if current_os == 'Linux':
        target = linux_playing.is_now_playing
    if current_os == 'Darwin':
        target = mac_playing.is_now_playing
    if current_os == 'Windows':
        target = windows_playing.is_now_playing

    t = threading.Thread(target=target, args=(interval,))
    t.daemon = daemon
    t.start()
