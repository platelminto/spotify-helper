import zope.event
import threading
import platform
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def fire_when_playing(event):

    print('wooooo')


def start_listening(interval, daemon=True):

    zope.event.subscribers.append(fire_when_playing)

    current_os = platform.system()

    if current_os == 'Linux':
        import linux_playing
        target = linux_playing.is_now_playing
    if current_os == 'Darwin':
        import mac_playing
        target = mac_playing.is_now_playing
    if current_os == 'Windows':
        import windows_playing
        target = windows_playing.is_now_playing

    t = threading.Thread(target=target, args=(interval,))
    t.daemon = daemon
    t.start()
