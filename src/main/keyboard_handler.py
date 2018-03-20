import sys

import os

from pynput.keyboard import Key, KeyCode, Listener

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from main.save_song import SpotifySaveSong

options_file = '../options.txt'


class KeyboardHandler:

    def __init__(self):
        self.spotify_save_song = SpotifySaveSong()

        self.currently_pressed_keys = set()
        self.looking_for = set()

        for key_str in SpotifySaveSong.read_option('key_combo').split('+'):
            self.looking_for.add(self.get_key_from_string(key_str))

    @staticmethod
    def get_key_from_string(key_str):

        try:
            return getattr(Key, key_str)
        except AttributeError:
            return KeyCode.from_char(key_str)

    def on_press(self, key):
        self.currently_pressed_keys.add(key)

        if self.looking_for == self.currently_pressed_keys:
            self.spotify_save_song.save_song()
            self.currently_pressed_keys.clear()

    def on_release(self, key):
        try:
            self.currently_pressed_keys.remove(key)
        except KeyError:
            pass


keyboard = KeyboardHandler()

with Listener(on_press=keyboard.on_press, on_release=keyboard.on_release) as listener:
    listener.join()
