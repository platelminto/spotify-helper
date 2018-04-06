import sys

import os

from pynput.keyboard import Key, KeyCode, Listener

from main.notif_handler import send_notif

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from spotify_api.spotify import Spotify

options_file = '../options.txt'
bindings_file = '../bindings.txt'

spotify = Spotify()

currently_pressed_keys = list()
looking_for = {}


def get_key_from_string(key_str):

    try:
        return getattr(Key, key_str)
    except AttributeError:
        return KeyCode.from_char(key_str)


def on_press(key):
    currently_pressed_keys.append(key)

    for func_name, key_set in looking_for.items():
        if currently_pressed_keys == key_set:

            try:
                getattr(spotify, func_name)()

            except ConnectionError:
                send_notif('Connection Error', 'Internet connection not available')

            currently_pressed_keys.pop(-1)


def on_release(key):
    try:
        currently_pressed_keys.remove(key)
    except ValueError:
        pass


with open(bindings_file) as file:

    for line in file:
        line = line.rstrip()
        name, binding = line.split('=')[0], line.split('=')[-1]

        if binding is not '':
            keys = list()
            for single_key in binding.split('+'):
                keys.append(get_key_from_string(single_key))

            looking_for[name] = keys

with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
