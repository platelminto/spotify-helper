Easily save songs currently playing from Spotify to your library using a hotkey or key combo. (Currently only f8, will make this easily editable). Only on linux for now.

Make a keys.txt file in the src/ directory, with client_id & secret obtained from making an API application [here](https://beta.developer.spotify.com/dashboard/applications), putting them on the first and second line of the file, respectively. 

On first run, a browser window should open and the url should point to localhost, with a single `code` paramater: copy its value into the commandline (which should be awaiting input).
