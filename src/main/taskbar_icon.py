import os
import sys
import threading
import time
import webbrowser

from PIL import Image
from pystray import Icon, Menu, MenuItem


# Begins the keyboard listener.
class SpotifyThread(threading.Thread):
    def __init__(self):
        super(SpotifyThread, self).__init__()
        self.daemon = True

    def run(self):
        import src.main.spotify_helper


auth_checker_thread = SpotifyThread()
auth_checker_thread.start()


# Opens the bindings file in the default text editor (not in a web browser)
def open_bindings_file():
    webbrowser.open('../bindings.txt')


if __name__ == "__main__":
    authenticated = False

    icon_image = Image.open('../resources/spo.png')

    icon = Icon('spotify-helper', icon_image, menu=Menu(
        MenuItem(
            text='Edit bindings',
            action=open_bindings_file),
        Menu.SEPARATOR,
        MenuItem(
            text='Quit',
            action=lambda: sys.exit(0)
        ),
    ))
    icon.run()