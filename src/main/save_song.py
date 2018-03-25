import sys

import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from spotify_api.spotify import Spotify
from main import notif_handler

options_file = '../options.txt'


class SpotifySaveSong:

    def __init__(self):

        self.spotify = Spotify()

    def save(self):
        song_id = self.spotify.currently_playing_id()

        if song_id:

            is_saved = self.spotify.is_saved(song_id)

            if is_saved:

                notif_handler.make_notif(self.spotify.remove_songs_from_library(song_id),
                                         'removed from', 'remove from')

            else:

                notif_handler.make_notif(self.spotify.add_songs_to_library(song_id), 'added to', 'add to')

    def save_playlist(self):
        pass

    def next(self):
        self.spotify.next_song()

    def previous(self):
        pass

    def pause(self):
        pass

    def toggle_play(self):
        pass

    def play(self):
        pass

    def toggle_repeat(self):
        pass

    def toggle_shuffle(self):
        pass