import sys

import os
import traceback

from pynput.keyboard import Key, KeyCode, Listener

from main.notif_handler import send_notif

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from spotify_api.spotify import Spotify

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

    for key_tuple, methods in looking_for.items():
        if currently_pressed_keys == list(key_tuple):

            try:
                for method in methods:
                    getattr(spotify, method)()

            except ConnectionError:
                send_notif('Connection Error', 'Internet connection not available')
            except Exception as e:
                send_notif('Error', 'Something went wrong')
                print(e)
                traceback.print_tb(e.__traceback__)

            currently_pressed_keys.pop(-1)


def on_release(key):
    try:
        currently_pressed_keys.remove(key)
    except ValueError:
        pass


with open(bindings_file) as file:

    for line in file:
        method_and_keycodes = line.split('=')

        method = method_and_keycodes[0]
        rest_of_line = method_and_keycodes[1]

        if '#' in rest_of_line:

            rest_of_line = rest_of_line[:rest_of_line.index('#')]

        bindings = rest_of_line.rstrip()

        if bindings is not '':
            for binding in bindings.split(','):
                keys = list()
                for single_key in binding.split('+'):
                    keys.append(get_key_from_string(single_key))

                keys_tuple = tuple(keys)

                if keys_tuple not in looking_for.keys():
                    looking_for[keys_tuple] = []

                looking_for[keys_tuple].append(method)


with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
