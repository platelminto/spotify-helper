import requests
import time
import webbrowser
import base64
import json


class WebApi:

    def __init__(self, scope_list, client_id, client_secret, redirect_uri):

        self.auth_keys_path = '../auth.txt'

        self.api_url = 'https://api.spotify.com/v1/'
        self.authorize_access_url = 'https://accounts.spotify.com/authorize/'
        self.get_token_url = 'https://accounts.spotify.com/api/token'

        self.scope_list = scope_list
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

        try:
            self.file = open(self.auth_keys_path, 'r+')

            self.load_auth_values(self.file)

            self.check_for_refresh_token(self.file, self.expiry_time)

        except (FileNotFoundError, ValueError):
            self.write_auth_info()

        self.file.close()

    def write_auth_info(self):

        self.file = open(self.auth_keys_path, 'w+')
        current_time = time.time()
        info = self.get_access_info(self.get_auth_code())

        self.save_auth_values(self.file, info.get('access_token'), info.get('refresh_token'),
                          current_time + info.get('expires_in'))

    def check_for_refresh_token(self, file, expiry_time):

        if time.time() > expiry_time:

            self.refresh_tokens(file)

    def get_auth_code(self):

        params = {'client_id': self.client_id, 'response_type': 'code', 'redirect_uri': self.redirect_uri,
                  'scope': ' '.join(self.scope_list)}

        r = requests.get(self.authorize_access_url, params=params)

        webbrowser.open_new(r.url)

        return input('input code: ')

    def get_access_info(self, auth_code):

        payload = {'grant_type': 'authorization_code', 'code': auth_code,
                   'redirect_uri': self.redirect_uri, 'client_id': self.client_id,
                   'client_secret': self.client_secret}

        r = requests.post(self.get_token_url, data=payload)

        return r.json()

    def refresh_tokens(self, file):

        payload = {'grant_type': 'refresh_token', 'refresh_token': self.refresh_token}

        headers = {'Authorization': 'Basic ' + base64.b64encode(
            (self.client_id + ':' + self.client_secret).encode('ascii')).decode('ascii')}

        obtained_time = time.time()

        r = requests.post(self.get_token_url, data=payload, headers=headers)

        info = r.json()

        if r.status_code == 401:
            self.write_auth_info()

        if 'refresh_token' in info:
            self.refresh_token = info.get('refresh_token')

        self.save_auth_values(file, info.get('access_token'), self.refresh_token,
                              obtained_time + info.get('expires_in'))
        self.load_auth_values(file)

    def save_auth_values(self, file, access_token, refresh_token, expiry_time):

        file.seek(0)

        file.write(access_token + '\n')
        file.write(refresh_token + '\n')
        file.write(str(expiry_time) + '\n')

        self.load_auth_values(file)

    def load_auth_values(self, file):

        file.seek(0)

        self.access_token = file.readline().rstrip('\n')
        self.refresh_token = file.readline().rstrip('\n')
        self.expiry_time = float(file.readline().rstrip('\n'))

        print('authenticated')

    def get_access_header(self):

        file = open(self.auth_keys_path, 'r+')

        self.check_for_refresh_token(file, self.expiry_time)

        file.close()

        return {'Authorization': 'Bearer ' + self.access_token}

    @staticmethod
    def check_status_code(r):
        code = r.status_code

        if code > 300:
            print(code)
            return None

        return r

    def get(self, endpoint, params=None):

        r = self.check_status_code(requests.get(self.api_url + endpoint,
                                                params=params, headers=self.get_access_header()))

        return r

    def post(self, endpoint, payload=None):

        r = self.check_status_code(requests.post(self.api_url + endpoint,
                                                 data=json.dumps(payload), headers=self.get_access_header()))
        return r

    def put(self, endpoint, data=None):

        r = self.check_status_code(requests.put(self.api_url + endpoint,
                                                data=json.dumps(data), headers=self.get_access_header()))
        return r

    def delete(self, endpoint, payload=None):

        r = self.check_status_code(requests.delete(self.api_url + endpoint,
                                                   headers=self.get_access_header(), data=json.dumps(payload)))
        return r
