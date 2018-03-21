import sys

import os

from pynput.keyboard import Key, KeyCode, Listener

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from main.save_song import SpotifySaveSong

options_file = '../options.txt'

spotify_save_song = SpotifySaveSong()

currently_pressed_keys = set()
looking_for = set()


def get_key_from_string(key_str):

    try:
        return getattr(Key, key_str)
    except AttributeError:
        return KeyCode.from_char(key_str)


def on_press(key):
    currently_pressed_keys.add(key)

    if looking_for == currently_pressed_keys:
        spotify_save_song.save_song()
        currently_pressed_keys.clear()


def on_release(key):
    try:
        currently_pressed_keys.remove(key)
    except KeyError:
        pass


for key_str in SpotifySaveSong.read_option('key_combo').split('+'):
    looking_for.add(get_key_from_string(key_str))


with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
