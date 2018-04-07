## spotify-helper
Provides various utility methods to interact with Spotify, mostly through the ability to assign keyboard shortcuts to most Spotify functions. These are editable in the `options.txt` file. Run `main/keyboard_handler.py` with python 3 to start the script (has to be run as sudo on macOS for keyboard access).

The program first tries to directly interact with the Spotify client (unavailable on Windows), and then falls back on using the Web API; some methods are only available using the Web API.

For this, Spotify developer API keys are required: make a `keys.txt` file in the `src/` directory, with your client id & client secret on the first and second lines of the file. They can be obtained from making an API application [here](https://beta.developer.spotify.com/dashboard/applications). Additionally, in the application dashboard, go to 'Edit Settings', and set the redirect URI to 'http://localhost:8888/callback'

On first run, a browser window should open asking for your Spotify accounts' permission to let the app handle parts of your account - after accepting, the url should point to localhost, with a single `code` parameter: copy its value into the commandline (which should be awaiting input). From then on, nothing other than starting up the script should be required.

### Dependencies

To install all the dependencies needed, find the appropriate requirements text file for your OS in `requirements/`, and run:

`pip install -r requirements.txt`

They are also listed below, together with a link to their site & how they are used:

#### For all OSes

- [Requests](http://docs.python-requests.org/en/master/) - to communicate easily with the Spotify API service.
- [pynput](https://pythonhosted.org/pynput/) - to read keyboard input regardless of platform.

#### Windows

- [pywin32](https://pypi.python.org/pypi/pywin32) - to be able to send notifications on Windows.
