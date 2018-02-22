import sys
import os

import keyboard
import notify2
import gi

gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import spotify_api.spotify as spotify

if __name__ == '__main__':
    pass

def saveSong():
    
    songId = spotify.currentlyPlayingId()
    
    isSaved = spotify.isSaved(songId)
    
    if isSaved:
        
        sendNotif(spotify.removeSongsFromLibrary(songId), 'removed from', 'remove from')
        
    else:
        
        sendNotif(spotify.addSongsToLibrary(songId), 'added to', 'add to')

def sendNotif(success, successString, failString):
    
    notify2.init('')
    
    if(success):
        
        n = notify2.Notification('Success', 'Successfully ' + successString + ' library')
    
    else:
        
        n = notify2.Notification('Failed', 'Failed to ' + failString + ' library')
    
    n.set_icon_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file('../resources/spotify.png'))
    n.set_timeout(3100)
    n.show()
    
keyboard.add_hotkey('f8', lambda: saveSong())
keyboard.wait('esc')