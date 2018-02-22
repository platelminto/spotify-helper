import requests
import time
import webbrowser
import base64
import json
from json.decoder import JSONDecodeError
from pathlib import Path

auth_keys_path = str(Path.home()) + '/.auth.txt'

api_url = 'https://api.spotify.com/v1/'
authorize_access_url = 'https://accounts.spotify.com/authorize/'
get_token_url = 'https://accounts.spotify.com/api/token'

scope_list = ['user-library-read', 'user-library-modify', 'user-read-currently-playing']

class SpotifyApi(object):
    
    def __init__(self, scope_list, client_id, client_secret, redirect_uri):
        
        self.scope_list = scope_list
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
        try:
            file = open(auth_keys_path, 'r+')
            self.load_auth_values(file)
            
            self.check_for_refresh_token(file, self.obtained_time, self.duration)
        
        except (FileNotFoundError, ValueError):
            file = open(auth_keys_path, 'w+')
            current_time = time.time()
            info = self.get_access_info(self.get_auth_code())
            
            self.save_auth_values(file, info.get('access_token'), info.get('refresh_token'), 
                                  current_time, info.get('expires_in'))
    
        file.close()
        
    def check_for_refresh_token(self, file, obtained_time, duration):
        
        if time.time() - obtained_time > duration:
                
            self.refresh_tokens(file)
    
    def get_auth_code(self):
        
        params = {'client_id': self.client_id, 'response_type': 'code', 'redirect_uri': self.redirect_uri,
              'scope': ' '.join(scope_list)}
    
        r = requests.get(authorize_access_url, params=params)
    
        webbrowser.open_new(r.url)
    
        return input('input code: ')
    
    def get_access_info(self, auth_code):
        
        payload = {'grant_type': 'authorization_code', 'code': auth_code,
                  'redirect_uri': self.redirect_uri, 'client_id': self.client_id, 
                  'client_secret': self.client_secret}
        
        r = requests.post(get_token_url, data=payload)
        
        return r.json()
    
    def refresh_tokens(self, file):
        
        payload = {'grant_type': 'refresh_token', 'refresh_token': self.refresh_token}
        
        headers = {'Authorization': 'Basic ' + base64.b64encode((self.client_id + ':' + self.client_secret).encode('ascii')).decode('ascii')}
    
        info = requests.post(get_token_url, data=payload, headers=headers).json()
        
        if 'refresh_token' in info:
            
            self.refresh_token = info.get('refresh_token')
            
        self.save_auth_values(file, info.get('access_token'), self.refresh_token, time.time(), info.get('expires_in'))
        self.load_auth_values(file)
        
    def save_auth_values(self, file, access_token, refresh_token, obtained_time, duration):
        
        file.seek(0)
        
        file.write(access_token + '\n')
        file.write(refresh_token + '\n')
        file.write(str(obtained_time) + '\n')
        file.write(str(duration))
        
        self.load_auth_values(file)
        
    def load_auth_values(self, file):
        
        file.seek(0)
        
        self.access_token = file.readline().rstrip('\n')
        self.refresh_token = file.readline().rstrip('\n')
        self.obtained_time = float(file.readline().rstrip('\n'))
        self.duration = float(file.readline().rstrip('\n'))
        
    def get_access_header(self):
        
        file = open(auth_keys_path)
        
        self.check_for_refresh_token(file, self.obtained_time, self.duration)
        
        file.close()
        
        return {'Authorization': 'Bearer ' + self.access_token}
    
    def get(self, endpoint, params=None):
        
        r = requests.get(api_url + endpoint, params=params, headers=self.get_access_header())
        
        try:
            return r.json()
        except JSONDecodeError:
            return r
   
    def post(self, endpoint, payload=None):
        
        r = requests.post(api_url + endpoint, data=payload, headers=self.get_access_header())
    
        try:
            return r.json()
        except JSONDecodeError:
            return r
        
    def put(self, endpoint, data=None):
        
        r = requests.put(api_url + endpoint, data=json.dumps(data), headers=self.get_access_header())
    
        try:
            return r.json()
        except JSONDecodeError:
            return r
        
    def delete(self, endpoint, data=None):
        
        r = requests.delete(api_url + endpoint, headers=self.get_access_header(), data=json.dumps(data))
        
        try:
            return r.json()
        except JSONDecodeError:
            return r