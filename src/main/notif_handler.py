import platform
import os

current_os = platform.system()

notif_icon_path = os.path.abspath('../resources/spotify.ico')
notif_duration_ms = 3100

if current_os == 'Linux':

    import dbus

if current_os == 'Windows':

    import threading
    import main.windows_notif as windows_notif


def windows_notify(title, text, icon_path, duration):
    t = threading.Thread(target=windows_notif.send_notif, args=(title, text, icon_path, duration))
    t.daemon = True
    t.start()


def apple_notify(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))


def linux_notify(title, text, icon_path, duration):

    bus = dbus.SessionBus()

    notify = bus.get_object('org.freedesktop.Notifications', '/org/freedesktop/Notifications')
    method = notify.get_dbus_method('Notify', 'org.freedesktop.Notifications')

    method("save-song-spotify", 24, icon_path, title, text, [], [], duration)


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
