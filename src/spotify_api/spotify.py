from spotify_api.api import SpotifyApi

if __name__ == '__main__':
    pass

client_id = '88596666d75941c3abb43ab8a1b67b8f'
client_secret = '4406a158a41045ccb6e013cd8756b0db'
redirect_uri = 'http://localhost:8888/callback'

scope_list = ['user-library-read', 'user-library-modify', 'user-read-currently-playing']

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