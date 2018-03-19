from pynput.keyboard import Key, KeyCode

from main.spotify_save_song import read_option


class KeyboardHandler:

    def __init__(self):
        self.currently_pressed_keys = set()

        self.looking_for = set()

        for key_str in read_option('key_combo').split('+'):
            self.looking_for.add(self.get_key_from_string(key_str))

    @staticmethod
    def get_key_from_string(key_str):

        try:
            return getattr(Key, key_str)
        except AttributeError:
            return KeyCode.from_char(key_str)

    def on_press(self, func, key):
        self.currently_pressed_keys.add(key)

        if self.looking_for == self.currently_pressed_keys:
            func()
            self.currently_pressed_keys.clear()

    def on_release(self, key):
        try:
            self.currently_pressed_keys.remove(key)
        except KeyError:
            pass
