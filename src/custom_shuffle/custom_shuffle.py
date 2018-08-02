import sys
import os
import platform
import random

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from has_song_changed import HasSongChanged


NEXT_SONG_STRICTNESS = 5


def create_shuffled_list(unshuffled_list):

    shuffled_list = list()
    remaining = len(unshuffled_list)

    for _ in unshuffled_list:

        random_index = random.randrange(0, remaining)

        shuffled_list.append(unshuffled_list[random_index])
        unshuffled_list[random_index], unshuffled_list[remaining-1] = unshuffled_list[remaining-1], unshuffled_list[random_index]

        remaining = remaining - 1

    return shuffled_list


class CustomShuffle:

    def __init__(self):

        self.song_changed = HasSongChanged(5, self.has_taken_over, False)
        self.shuffled_list = list()
        self.current_list_counter = 0

        self.os = platform.system()

    def enable(self):

        self.song_changed.start_listening()

    def disable(self):

        self.song_changed.stop_listening()

    def has_taken_over(self, song_id):  # Called when song changes, arguments already provided

        try:
            if song_id in self.shuffled_list[self.current_list_counter + 1:self.current_list_counter + 1 + NEXT_SONG_STRICTNESS]:

                self.current_list_counter = self.shuffled_list.index(song_id)
                return

            raise IndexError

        except IndexError:

            self.reshuffle_playlist()

    def reshuffle_playlist(self):

        pass

    def is_cache_updated(self):

        pass

    def get_playlist_from_web(self):

        pass

    def send_custom_shuffle(self):

        pass
