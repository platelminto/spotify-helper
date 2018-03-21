import platform

current_os = platform.system()


def get_track_id():

    if current_os == 'Linux':
        return get_track_id_linux()

    if current_os == 'Darwin':
        return get_track_id_mac()

    raise ModuleNotFoundError


def get_track_id_linux():
    import dbus

    try:
        session_bus = dbus.SessionBus()
        spotify_bus = session_bus.get_object("org.mpris.MediaPlayer2.spotify",
                                             "/org/mpris/MediaPlayer2")
        spotify_properties = dbus.Interface(spotify_bus,
                                            "org.freedesktop.DBus.Properties")
        metadata = spotify_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")
    except dbus.DBusException:
        raise ModuleNotFoundError

    return metadata.get('mpris:trackid').split(':')[-1]


def get_track_id_mac():
    import subprocess

    result = subprocess.run(['osascript', '-e',
                             'tell application "Spotify" \n\treturn id of current track as string \nend tell'],
                            stdout=subprocess.PIPE)

    if result.returncode is not 0:
        raise ModuleNotFoundError

    return result.stdout.decode('utf-8').rstrip().split(':')[-1]
