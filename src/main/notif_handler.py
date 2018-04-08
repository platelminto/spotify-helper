import platform
import os
import tempfile
from urllib.request import urlopen, URLError

current_os = platform.system()

notif_icon_path = os.path.abspath('../resources/spotify.ico')
notif_duration_ms = 3750

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


def send_notif(title, text, icon_path=notif_icon_path):

    if current_os == 'Linux':

        linux_notify(title, text, icon_path, notif_duration_ms)

    elif current_os == 'Darwin':

        apple_notify(title, text)

    elif current_os == 'Windows':

        windows_notify(title, text, icon_path, notif_duration_ms)


def send_notif_with_web_image(title, text, image_url, timeout=0.75):

    if image_url is None:
        send_notif(title, text)
        return

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
