import zope.event
import threading
import platform


class HasSongChanged:

    def __init__(self, interval, func, daemon=True):

        zope.event.subscribers.append(self.fire_when_playing)

        self.current_os = platform.system()
        self.func = func
        self.interval = interval
        self.daemon = daemon

        if self.current_os == 'Linux':
            import linux_has_song_changed
            self.has_song_changed = linux_has_song_changed

        if self.current_os == 'Darwin':
            import mac_has_song_changed
            self.has_song_changed = mac_has_song_changed

        if self.current_os == 'Windows':
            import windows_has_song_changed
            self.has_song_changed = windows_has_song_changed

    def fire_when_playing(self, event):

        self.func(str(event))

    def start_listening(self):

        t = threading.Thread(target=self.has_song_changed.has_song_changed, args=(self.interval,))
        t.daemon = self.daemon
        t.start()

    def stop_listening(self):

        self.has_song_changed.stop_listening()
