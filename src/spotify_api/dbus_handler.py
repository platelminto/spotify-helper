import dbus


class DbusHandler:

    def __init__(self):
        session_bus = dbus.SessionBus()
        spotify_bus = session_bus.get_object("org.mpris.MediaPlayer2.spotify",
                                             "/org/mpris/MediaPlayer2")
        spotify_properties = dbus.Interface(spotify_bus,
                                            "org.freedesktop.DBus.Properties")
        self.metadata = spotify_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")

    def get_track_id(self):
        return self.metadata.get('mpris:trackid')

    def print_metadata(self):

        for key, value in self.metadata.items():
            print(key, value)
