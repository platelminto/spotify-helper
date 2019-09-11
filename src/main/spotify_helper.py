# Main program, starts the keyboard listening.

import sys

import os
import traceback

import requests
from pynput.keyboard import Key, KeyCode, Listener

# Needed for the program to work from an IDE and from the commandline.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from spotify_api.spotify import Spotify
from notifications.notif_handler import send_notif

bindings_file = '../bindings.txt'

try:
    spotify = Spotify()
except requests.exceptions.ConnectionError:
    send_notif('Spotify Helper closed', 'Check you have a working internet connection.')
    sys.exit(1)

currently_pressed_keys = list()
looking_for = {}


# Get pynput key from a string - modifier keys are captured in the try statement,
# while normal letter keys are obtained from the KeyCode.from_char() method.
def get_key_from_string(key_str):
    try:
        return getattr(Key, key_str)

    except AttributeError:
        return KeyCode.from_char(key_str)


with open(bindings_file) as file:
    for line in file:
        method_and_keycodes = line.split('=')

        method = method_and_keycodes[0]  # The method to run
        rest_of_line = method_and_keycodes[1]  # Includes bindings we have to parse

        # Allows comments in the bindings file
        if '#' in rest_of_line:
            rest_of_line = rest_of_line[:rest_of_line.index('#')]

        bindings = rest_of_line.rstrip()

        if bindings is not '':
            # Can have multiple bindings split by commas.
            for binding in bindings.split(','):
                keys = list()
                for single_key in binding.split('+'):
                    keys.append(get_key_from_string(single_key))

                keys_tuple = tuple(keys)

                # looking_for is a dictionary where the keys are the bindings and the values
                # are all the methods linked to those keys, as you can have multiple bindings
                # per method and vice versa.

                if keys_tuple not in looking_for.keys():
                    looking_for[keys_tuple] = []

                looking_for[keys_tuple].append(method)


def on_press(key):
    # Keys are unique in each binding, as it makes no sense to have ctrl+ctrl+f5, for example.
    # Also prevents the same key being added more than once if held down too long, which happens
    # on some systems.
    if key not in currently_pressed_keys:
        currently_pressed_keys.append(key)

    for key_tuple, methods in looking_for.items():
        if currently_pressed_keys == list(key_tuple):
            for method in methods:
                try:
                    getattr(spotify, method)()

                except ConnectionError:
                    send_notif('Connection Error', 'Internet connection not available')
                except Exception as e:
                    send_notif('Error', 'Something went wrong')
                    print(e)
                    traceback.print_tb(e.__traceback__)

            # Remove the last element so, to run the same binding again, the user must
            # repress the last key (to avoid rerunning methods on the same key presses).
            currently_pressed_keys.pop(-1)


def on_release(key):
    try:
        currently_pressed_keys.remove(key)

    except ValueError:  # Sometimes it's already empty so raises this exception, to be ignored.
        pass


# Begins the keyboard listener.
with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
