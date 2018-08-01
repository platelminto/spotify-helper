import sys
import os
import platform

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from has_song_changed import HasSongChanged


class CustomShuffle:

    def __init__(self):

        self.song_changed = HasSongChanged(5, self.has_taken_over, False)
        self.shuffle_list = list()

        self.os = platform.system()

    def enable(self):

        self.song_changed.start_listening()

    def disable(self):

        self.song_changed.stop_listening()

    def has_taken_over(self, song_id):  # Called when song changes, arguments already provided

        print(song_id)

    def is_currently_playing_still_correct(self):

        pass

    def is_cache_updated(self):

        pass

    def get_playlist_from_web(self):

        pass


cs = CustomShuffle()
cs.enable()
