from json import JSONDecodeError

from spotify_api.api import SpotifyApi

if __name__ == '__main__':
    pass

keys_file = open('../keys.txt')

client_id = keys_file.readline().rstrip()
client_secret = keys_file.readline().rstrip()

keys_file.close()

redirect_uri = 'http://localhost:8888/callback'

scope_list = ['user-library-read', 'user-library-modify', 'user-read-currently-playing']

api = SpotifyApi(scope_list=scope_list, client_id=client_id, 
                 client_secret=client_secret, redirect_uri=redirect_uri)


def check_status_code(r):

    code = r.status_code

    if code > 300:
        print(code)
        if code == 400:
            print('Malformed request')
        elif code == 401:
            print('Refreshing tokens, try again')
            with open(api.auth_keys_path, 'w+') as file:
                api.refresh_tokens(file)
        return None

    else:
        try:
            return r.json()
        except JSONDecodeError:
            return r


def add_songs_to_library(*song_ids):
    return api.put('me/tracks', data={'ids': song_ids})


def currently_playing_id():
    return api.get('me/player/currently-playing').get('item').get('id')


def is_saved(song_id):
    return api.get('me/tracks/contains?ids=' + song_id)[0]


def remove_songs_from_library(*song_ids):
    return api.delete('me/tracks', payload={'ids': song_ids})