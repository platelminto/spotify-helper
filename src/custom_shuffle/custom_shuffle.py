import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from custom_shuffle import HasSongChanged


class CustomShuffle:

    def __init__(self):

        self.song_changed = HasSongChanged(5, self.has_taken_over)
        self.shuffle_list = list()

    def enable(self):

        self.song_changed.start_listening()

    def disable(self):

        self.song_changed.stop_listening()

    def has_taken_over(self):

        pass

    def is_song_in_playlist(self):

        pass

    def is_cache_updated(self):

        pass

