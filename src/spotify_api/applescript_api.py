import subprocess


class AppleScriptApi:

    @staticmethod
    def run_command(command):

        result = subprocess.run(['osascript', '-e',
                                 'tell application "Spotify" to ' + command],
                                stdout=subprocess.PIPE)

        if result.returncode is not 0:
            raise NameError

        return result.stdout.decode('utf-8').rstrip()

    @staticmethod
    def get_track_id():

        result = AppleScriptApi.run_command('return id of current track as string')

        return result.split(':')[-1]

    @staticmethod
    def get_album():

        return AppleScriptApi.run_command('return album of current track')

    @staticmethod
    def get_track():

        return AppleScriptApi.run_command('return name of current track')

    @staticmethod
    def get_artist():

        return AppleScriptApi.run_command('return artist of current track')

    @staticmethod
    def get_art_url():

        return AppleScriptApi.run_command('return artwork url of current track')

    @staticmethod
    def get_current_track():

        track = dict()
        track['name'] = AppleScriptApi.get_track()
        track['artists'] = [{'name': AppleScriptApi.get_artist()}]
        track['album'] = {'name': AppleScriptApi.get_album(), 'images': [{'url': AppleScriptApi.get_art_url()}]}

        return track

    @staticmethod
    def play_pause():

        return AppleScriptApi.run_command('playpause')

    @staticmethod
    def next():

        return AppleScriptApi.run_command('next track')

    @staticmethod
    def previous():

        return AppleScriptApi.run_command('previous track')

    @staticmethod
    def stop():

        return AppleScriptApi.run_command('pause')

    @staticmethod
    def pause():

        return AppleScriptApi.run_command('pause')

    @staticmethod
    def play():

        return AppleScriptApi.run_command('play')
