## spotify-save-song
Easily save songs currently playing from Spotify to your library using a hotkey or key combo, editable in the `options.txt` file - defaults to left-control + f8. Run `main/keyboard_handler.py` to start the script (has to be run as sudo on macOS, to be able to access raw keyboard inputs).

Make a keys.txt file in the src/ directory, with client id & secret obtained from making an API application [here](https://beta.developer.spotify.com/dashboard/applications), putting them on the first and second line of the file, respectively. In the application dashboard, go to 'Edit Settings', and set the redirect URI to 'http://localhost:8888/callback'

On first run, a browser window should open and the url should point to localhost, with a single `code` parameter: copy its value into the commandline (which should be awaiting input). From then on, nothing other than starting up the script should be required by the user.

Enabling the `'monthly_playlist'` option in `options.txt` also adds saved songs to a monthly playlist (for example, 'March 2018'), and creates one if there isn't one available.

### Dependencies
#### General

- [Requests](http://docs.python-requests.org/en/master/)
- [pynput](https://pythonhosted.org/pynput/)

#### Windows

- [pywin32](https://pypi.python.org/pypi/pywin32)
