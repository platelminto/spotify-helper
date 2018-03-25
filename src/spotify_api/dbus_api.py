import platform
import dbus


class DBusApi:

    def __init__(self):

        self.current_os = platform.system()
        self.player = 'org.mpris.MediaPlayer2.Player'

        session_bus = dbus.SessionBus()
        self.spotify_bus = session_bus.get_object('org.mpris.MediaPlayer2.spotify',
                                                  '/org/mpris/MediaPlayer2')
        self.spotify_properties = dbus.Interface(self.spotify_bus,
                                                 'org.freedesktop.DBus.Properties')
        self.metadata = self.spotify_properties.Get(self.player, 'Metadata')

        self.interface = dbus.Interface(self.spotify_bus, self.player)

    # Spotify doesn't support the majority of available properties
    def get_property(self, player_propety):

        return self.spotify_properties.Get(self.player, player_propety)

    # Same as above
    def set_property(self, player_propety, value):

        return self.spotify_properties.Set('org.mpris.MediaPlayer2.Player', player_propety, value)

    def run_method(self, method_str, *args):

        return getattr(self.interface, method_str)(*args)

    def get_info(self, info_str):

        return self.metadata.get(info_str)

    def get_track_id(self):

        return self.get_info('mpris:trackid').split(':')[-1]

    def play_pause(self):

        return self.run_method('PlayPause')

    def next(self):

        return self.run_method('Next')

    def previous(self):

        return self.run_method('Previous')

    # Is the same as pause()
    def stop(self):

        return self.run_method('Stop')

    def pause(self):

        return self.run_method('Pause')

    def play(self):

        return self.run_method('Play')

    # Does nothing
    def seek(self, offset):

        return self.run_method('Seek', offset)

    def open(self, uri):

        return self.run_method('OpenUri', uri)
