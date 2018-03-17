from spotify_api.api import SpotifyApi

import datetime

if __name__ == '__main__':
    pass

keys_file = open('../keys.txt')

client_id = keys_file.readline().rstrip()
client_secret = keys_file.readline().rstrip()

keys_file.close()

redirect_uri = 'http://localhost:8888/callback'

scope_list = ['user-library-read', 'user-library-modify', 'user-read-currently-playing',
              'playlist-read-public', 'playlist-modify-public']

api = SpotifyApi(scope_list=scope_list, client_id=client_id,
                 client_secret=client_secret, redirect_uri=redirect_uri)


def fetch_user_id():
    return api.get('me').get('id')


def monthly_playlist_id():
    now = datetime.datetime.now()
    month, year = now.strftime('%B'), str(now.year)
    try:
        file = open('../month_id.txt', 'r')

        if file.readline().rstrip() == month + year:

            playlist_id = file.readline()

            if playlist_id != '':
                return playlist_id

        file.close()

        raise ValueError

    except (FileNotFoundError, ValueError):

        file = open('../month_id.txt', 'w+')

        file.write(month + year + '\n')
        file.write(fetch_playlist_id(month, year))

        file.close()

        return monthly_playlist_id()


def get_user_id():
    try:
        with open('../user_id.txt', 'r') as user_id:
            return user_id.readline()
    except FileNotFoundError:

        with open('../user_id.txt', 'w+') as user_id:
            user_id.write(fetch_user_id())

        return get_user_id()


def fetch_playlist_id(month, year):
    response = api.get('me/playlists', params={'limit': '10'})

    for playlist in response.get('items'):

        if str(playlist.get('name')).lower() == (month + ' ' + year).lower():
            return playlist.get('id')

    return api.post('users/' + get_user_id() + '/playlists',
                    payload={'name': (month.capitalize() + ' ' + year)}).get('id')


def add_songs_to_monthly_playlist(*song_ids):
    return api.post('users/' + get_user_id() + '/playlists/' + monthly_playlist_id() + '/tracks',
                    payload={'uris': song_ids})


def remove_song_from_monthly_playlist(song_id):
    return api.delete('users/' + get_user_id() + '/playlists/' + monthly_playlist_id() + '/tracks',
                      payload={'tracks': [{'uri': song_id}]})


def add_songs_to_library(*song_ids):
    return api.put('me/tracks', data={'ids': song_ids})


def currently_playing_id():
    return api.get('me/player/currently-playing').get('item').get('id')


def is_saved(song_id):
    return api.get('me/tracks/contains?ids=' + song_id)[0]


def remove_songs_from_library(*song_ids):
    return api.delete('me/tracks', payload={'ids': song_ids})
