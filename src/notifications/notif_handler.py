# Handles sending notifications on Windows, Mac, and Linux.

import platform
import os
import tempfile
from urllib.request import urlopen, URLError

current_os = platform.system()  # This method returns 'Darwin' for macs.

notif_icon_path = os.path.abspath('../resources/spotify.ico')
notif_duration_ms = 3750

if current_os == 'Linux':
    import dbus

if current_os == 'Windows':
    import threading
    import main.windows_notif as windows_notif


def windows_notify(title, text, icon_path, duration):
    # Send the notifications from separate threads as there can be issues when sending
    # multiple notifications in quick succession.
    t = threading.Thread(target=windows_notif.send_notif, args=(title, text, icon_path, duration))
    t.daemon = True
    t.start()


def apple_notify(title, text):
    # Directly run AppleScript to send the notification - cannot set image for the notification
    # or its duration.
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))


def linux_notify(title, text, icon_path, duration):
    bus = dbus.SessionBus()

    notify = bus.get_object('org.freedesktop.Notifications', '/org/freedesktop/Notifications')
    notify = notify.get_dbus_method('Notify', 'org.freedesktop.Notifications')

    # The 2nd parameter being a 0 means this notification will not replace another (see
    # https://developer.gnome.org/notification-spec/) - the lists are for more
    # complex notifications and are therefore empty.
    notify("save-song-spotify", 0, icon_path, title, text, [], [], duration)


def send_notif(title, text, icon_path=notif_icon_path):
    if current_os == 'Linux':
        linux_notify(title, text, icon_path, notif_duration_ms)
    elif current_os == 'Darwin':
        apple_notify(title, text)
    elif current_os == 'Windows':
        windows_notify(title, text, icon_path, notif_duration_ms)


def send_notif_with_web_image(title, text, image_url, timeout=0.5):

    if image_url is None or current_os == 'Darwin':
        send_notif(title, text)
        return

    # We have to temporarily write the image contents to a file to use it in notifications.
    try:
        with urlopen(image_url, timeout=timeout) as response:
            data = response.read()

            file = tempfile.NamedTemporaryFile(delete=False)
            file.write(data)
            file.close()

            send_notif(title, text, file.name)

            os.unlink(file.name)

    except URLError:
        send_notif(title, text)
