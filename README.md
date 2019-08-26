## spotify-helper
Provides various utility methods to interact with Spotify, mostly through the ability to assign keyboard shortcuts to most Spotify functions. These are editable in the `bindings.txt` file. Run `spotify_helper.py` with python 3 to start the script (has to be run as sudo on macOS for keyboard access).

The program first tries to directly interact with the Spotify client (unavailable on Windows), and then falls back on using the Web API; some methods are only available using the Web API.

Since the Web API is always needed, Spotify developer API keys are required: in the `src/keys.txt` file, replace the placeholders on the first & second lines with your client id & client secret. They can be obtained from making an API application [here](https://developer.spotify.com/dashboard/applications). Additionally, in the application dashboard, go to 'Edit Settings', and set the redirect URI to 'http://localhost:8888/callback'

On first run, a browser window should open asking for your Spotify accounts' permission to let the app handle parts of your account - after accepting, the url should point to localhost, with a single `code` parameter: copy its value into the commandline (which should be awaiting input). From then on, nothing other than starting up the script should be required.

### Dependencies

To install all the dependencies needed, find the appropriate requirements text file for your OS in `requirements/`, and run:

`pip install -r requirements.txt`


#### General dependencies

- [Requests](http://docs.python-requests.org/en/master/) - to communicate easily with the Spotify API service.
- [pynput](https://pythonhosted.org/pynput/) - to read keyboard input regardless of platform.

#### Windows-specific dependencies

- [pywin32](https://pypi.python.org/pypi/pywin32) - to be able to send notifications on Windows.

#### Linux-specific dependencies

- [dbus-python](https://pypi.org/project/dbus-python) - to be able to interact with the Spotify client. **This dependency should already be installed on most Linux systems**, but if it isn't available, either install it from PyPI (`pip install dbus-python`) or, if you are using a virtual environment, copy the dbus python files from your system into the virtual environment's lib folder (as described [here](https://stackoverflow.com/a/23237728)).

