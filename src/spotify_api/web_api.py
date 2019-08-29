# Handles the authentication and communication with the Spotify Web API.

import os

import requests
import time
import webbrowser
import base64
import json
import threading


class WebApi:

    # This follows the 'Authorization Code Flow' path set out by
    # https://developer.spotify.com/documentation/general/guides/authorization-guide/#authorization-code-flow.
    def __init__(self, scope_list, client_id, client_secret, redirect_uri):
        self.online = True

        self.auth_keys_path = '../auth.txt'

        self.api_url = 'https://api.spotify.com/v1/'
        self.authorize_access_url = 'https://accounts.spotify.com/authorize/'
        self.get_token_url = 'https://accounts.spotify.com/api/token'

        self.scope_list = scope_list
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

        # First try and see if authentication tokens already exist, and if they do checks
        # whether they need to be refreshed.
        try:
            with open(self.auth_keys_path, 'r+') as file:
                self.load_auth_values(file)
                self.check_for_refresh_token(file, self.expiry_time)

        # If not, we need to obtain authorization from the user.
        except (FileNotFoundError, ValueError):
            self.write_auth_info()

        # Keeps checking if we're online or not to be able to refresh tokens and generally
        # contact the Web API.
        t = threading.Thread(target=self.check_online, args=(self.auth_keys_path,))
        t.daemon = True
        t.start()

    def write_auth_info(self):
        file = open(self.auth_keys_path, 'w+')
        current_time = time.time()
        info = self.get_access_info(self.get_auth_code())

        self.save_auth_values(file, info.get('access_token'), info.get('refresh_token'),
                              current_time + info.get('expires_in'))

    # The authorization keys need to be refreshed every once in a while
    def check_for_refresh_token(self, file, expiry_time):
        if time.time() > expiry_time and self.online:
            self.refresh_tokens(file)

    # This is how the user can authenticate themselves and must follow the instructions
    # in the README.
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

    def check_online(self, file_path):
        with open(file_path) as file:
            while True:
                time.sleep(10)

                if not self.online:
                    self.refresh_tokens(file)

    # Gets the new tokens after previous ones expire, following the format described by
    # the Spotify authorization guide.
    def refresh_tokens(self, file):
        payload = {'grant_type': 'refresh_token', 'refresh_token': self.refresh_token}
        headers = {'Authorization': 'Basic ' + base64.b64encode(
            (self.client_id + ':' + self.client_secret).encode('ascii')).decode('ascii')}
        obtained_time = time.time()

        try:
            r = requests.post(self.get_token_url, data=payload, headers=headers, timeout=4)
            self.online = True

        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            self.online = False
            return

        info = r.json()

        if 'error' in info:
            print('ERROR:', end=" ")
            if info.get('error') == 'invalid_client':
                print('Please set your client ID & secret in the src/keys.txt file, as described'
                      ' in the README.')
            else:
                print(info.get('error_description'))
            quit(1)

        # If we need additional permissions and have added them to the scope, the
        # old keys will not work, and we need new authentication info.
        if not set(info.get('scope').split(' ')).issuperset(set(self.scope_list)):
            self.write_auth_info()

        # 401 means there is a general unauthorized error, so we start anew with
        # the authentication process.
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

        self.access_token = file.readline().rstrip(os.linesep)
        self.refresh_token = file.readline().rstrip(os.linesep)
        self.expiry_time = float(file.readline().rstrip(os.linesep))

        print('authenticated')

    # The authorization values need to be in a specified header.
    def get_access_header(self):
        with open(self.auth_keys_path, 'r+') as file:
            self.check_for_refresh_token(file, self.expiry_time)

        return {'Authorization': 'Bearer ' + self.access_token}

    @staticmethod
    def check_status_code(r):
        code = r.status_code

        # These codes are error codes.
        if code >= 300:
            print(code)
            print(r.json().get('error').get('message'))
            if not (code == 403):
                raise Exception

        return r

    # The following functions are wrappers around requests' basic rest functions.

    def get(self, endpoint, params=None, timeout=4, retry=1):
        try:
            return self.check_status_code(requests.get(self.api_url + endpoint,
                                                       params=params, headers=self.get_access_header(),
                                                       timeout=timeout))

        except requests.exceptions.ConnectionError:
            if retry is not 0:
                return self.get(endpoint, params, timeout, retry - 1)
        except requests.exceptions.ReadTimeout:
            pass

        raise ConnectionError

    def post(self, endpoint, params=None, payload=None, timeout=4, retry=1):
        try:
            return self.check_status_code(requests.post(self.api_url + endpoint,
                                                        data=json.dumps(payload), params=params, headers=self.get_access_header(),
                                                        timeout=timeout))

        except requests.exceptions.ConnectionError:
            if retry is not 0:
                return self.get(endpoint, params, timeout, retry - 1)
        except requests.exceptions.ReadTimeout:
            pass

        raise ConnectionError

    def put(self, endpoint, params=None, payload=None, timeout=4, retry=1):
        try:
            return self.check_status_code(requests.put(self.api_url + endpoint,
                                                       data=json.dumps(payload), params=params, headers=self.get_access_header(),
                                                       timeout=timeout))

        except requests.exceptions.ConnectionError:
            if retry is not 0:
                return self.get(endpoint, params, timeout, retry - 1)
        except requests.exceptions.ReadTimeout:
            pass

        raise ConnectionError

    def delete(self, endpoint, params=None, payload=None, timeout=4, retry=1):
        try:
            return self.check_status_code(requests.delete(self.api_url + endpoint,
                                                          data=json.dumps(payload), params=params, headers=self.get_access_header(),
                                                          timeout=timeout))

        except requests.exceptions.ConnectionError:
            if retry is not 0:
                return self.get(endpoint, params, timeout, retry - 1)
        except requests.exceptions.ReadTimeout:
            pass

        raise ConnectionError
