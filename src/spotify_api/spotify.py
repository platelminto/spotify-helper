from spotify_api.api import SpotifyApi

import os
from pathlib import Path

if __name__ == '__main__':
    pass

keys_file = open('../keys.txt')

client_id = keys_file.readline()
client_secret = keys_file.readline()

keys_file.close()

redirect_uri = 'http://localhost:8888/callback'

scope_list = ['user-library-read', 'user-library-modify', 'user-read-currently-playing']

directory = str(Path.home()) + '/.spotify'

if not os.path.exists(directory):
    
    os.makedirs(directory)

api = SpotifyApi(scope_list=scope_list, client_id=client_id, 
                 client_secret=client_secret, redirect_uri=redirect_uri)

def addSongsToLibrary(*songIds):

    return api.put('me/tracks', data={'ids':songIds})
    
def currentlyPlayingId():
     
    return api.get('me/player/currently-playing').get('item').get('id')

def isSaved(songId):
    
    return api.get('me/tracks/contains?ids=' + songId)[0]
    
def removeSongsFromLibrary(*songIds):
    
    return api.delete('me/tracks', data={'ids':songIds})