from urllib import request
from urllib.error import HTTPError
from time import strftime
try:
    import simplejson as json
except ImportError:
    import json


class Scrobbler:

    def __init__(self, user):
        self.user = user
        self.api_key = '4829c7fa580a0b6c93f64610aeaf9e67'
        self.format = 'json'
        self.url = 'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&limit=1&user='+self.user+'&api_key='+self.api_key+'&format='+self.format
        self.request()
        self.get_playing()
        self.get_artist()
        self.get_title()

    def request(self):
        self.data = None
        try:
            response = request.urlopen(self.url)
            encoding = response.headers.get_content_charset()
            data = response.read().decode(encoding)
            self.data = json.loads(data)
        except HTTPError:
            Scrobbler.log('error', 'HTTP Error 503: Service Unavailable')
            pass
        return self.data

    def get_playing(self):
        self.np = False
        try:
            self.np = self.data['recenttracks']['track'][0]['@attr']['nowplaying']
        except KeyError:
            Scrobbler.log('error', 'KeyError occured.')
        finally:
            if self.np == 'true':
                self.np = True
            else:
                self.np = False
            return self.np

    def get_artist(self):
        self.artist = None
        if self.np:
            self.artist = self.data['recenttracks']['track'][0]['artist']['#text']
        return self.artist

    def get_title(self):
        self.title = None
        if self.np:
            self.title = self.data['recenttracks']['track'][0]['name']
        return self.title

    @classmethod
    def log(cls, level, message,):
        level = level.upper()
        time = strftime('%Y-%m-%d %H:%M:%S')
        print('%s [%s] [%s] %s' % (time, cls.__name__, level, message))
