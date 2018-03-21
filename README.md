## spotify-save-song
Easily save songs currently playing from Spotify to your library using a hotkey or key combo, editable in the `options.txt` file (defaults to left-control + f8). Run `main/keyboard_handler.py` with python 3 to start the script (has to be run as sudo on macOS for keyboard access)

Spotify developer API keys are required: make a `keys.txt` file in the `src/` directory, with your client id & client secret on the first and second lines of the file. They can be obtained from making an API application [here](https://beta.developer.spotify.com/dashboard/applications). Additionally, in the application dashboard, you have to go to 'Edit Settings', and set the redirect URI to 'http://localhost:8888/callback'

On first run, a browser window should open asking for your Spotify accounts' permission to let the app handle parts of your account - after accepting, the url should point to localhost, with a single `code` parameter: copy its value into the commandline (which should be awaiting input). From then on, nothing other than starting up the script should be required.

Enabling the `'monthly_playlist'` option in `options.txt` also adds saved songs to a monthly playlist (for example, 'March 2018'), and creates one if there isn't one available.

### Dependencies

To install all the dependencies needed, find the appropriate requirements text file for your OS in `requirements/`, and run:

`pip install -r requirements.txt`

#### For all OSes

- [Requests](http://docs.python-requests.org/en/master/)
- [pynput](https://pythonhosted.org/pynput/)

#### Windows

- [pywin32](https://pypi.python.org/pypi/pywin32)
