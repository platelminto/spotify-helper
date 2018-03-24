import subprocess

class AppleScriptApi:

    def get_track_id_mac(self):


        result = subprocess.run(['osascript', '-e',
                                 'tell application "Spotify" \n\treturn id of current track as string \nend tell'],
                                stdout=subprocess.PIPE)

        if result.returncode is not 0:
            raise ModuleNotFoundError

        return result.stdout.decode('utf-8').rstrip().split(':')[-1]