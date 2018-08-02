import zope.event
import threading
import platform
import os


def get_song_context(spotify_dir):

    for item in os.listdir(spotify_dir):
        if 'recently_played.bnk' in item:
            now_playing_file = item
            break

    with open(spotify_dir + '/' + now_playing_file, errors='replace') as playing_file:
        current_song_line = playing_file.readline()
        current_context_marker = 'spotify:'

        while current_context_marker not in current_song_line:
            current_song_line = playing_file.readline()

    id_beginning_index = current_song_line.find(current_context_marker) + len(current_context_marker)

    info = current_song_line[id_beginning_index:].split('$')[0].split(':')

    if info[0] == 'user':
        return info[2], info[3]

    else:
        return info[0], info[1]


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

    def get_song_context_id(self):

        return get_song_context(self.has_song_changed.get_spotify_dir())[1]

    def get_song_context_type(self):

        return get_song_context(self.has_song_changed.get_spotify_dir())[0]
