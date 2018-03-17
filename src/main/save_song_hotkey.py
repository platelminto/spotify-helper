import os
import sys
import platform
import time

from pynput.keyboard import Key, Listener

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
current_os = platform.system()

import spotify_api.spotify as spotify

if current_os == 'Linux':

    import dbus

if current_os == 'Windows':

    from win10toast import ToastNotifier

notif_icon_path = os.path.abspath('../resources/spotify.ico')
notif_duration_ms = 3100


def windows_notify(title, text, icon_path, duration):
    toaster = ToastNotifier()
    toaster.show_toast(title, text, icon_path=icon_path, duration=(duration/1000)-1, threaded=True)
    while toaster.notification_active():
        time.sleep(0.1)


def apple_notify(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))


def linux_notify(title, text, icon_path, duration):

    bus = dbus.SessionBus()

    notify = bus.get_object('org.freedesktop.Notifications', '/org/freedesktop/Notifications')
    method = notify.get_dbus_method('Notify', 'org.freedesktop.Notifications')

    method("easy-save-song-spotify", 24, icon_path, title, text, [], [], duration)


def save_song():
    song_id = spotify.currently_playing_id()

    is_saved = spotify.is_saved(song_id)

    if is_saved:

        spotify.remove_song_from_monthly_playlist('spotify:track:' + song_id)
        make_notif(spotify.remove_songs_from_library(song_id), 'removed from', 'remove from')

    else:

        spotify.add_songs_to_monthly_playlist('spotify:track:' + song_id)
        make_notif(spotify.add_songs_to_library(song_id), 'added to', 'add to')


def make_notif(success, success_string, fail_string):

    full_success_string = 'Successfully ' + success_string + ' library'
    full_fail_string = 'Failed to ' + fail_string + ' library'

    if success:

        send_notif('Success', full_success_string)

    else:

        send_notif('Failure', full_fail_string)


def send_notif(title, text):

    if current_os == 'Linux':

        linux_notify(title, text, notif_icon_path, notif_duration_ms)

    elif current_os == 'Darwin':

        apple_notify(title, text)

    elif current_os == 'Windows':

        windows_notify(title, text, notif_icon_path, notif_duration_ms)


def on_press(key):
    if key == Key.f8:
        save_song()


with Listener(on_press=on_press) as listener:
    listener.join()
