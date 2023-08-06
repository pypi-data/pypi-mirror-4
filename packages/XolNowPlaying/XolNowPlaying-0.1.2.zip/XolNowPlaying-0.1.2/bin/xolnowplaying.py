"""XolNowPlaying

Usage:
    xolnowplaying.py -u <user>
    xolnowplaying.py -u <user> -r <refresh_rate>
    xolnowplaying.py (-h | --help)
    xolnowplaying.py --version

Options:
    -h --help           Show this help
    --version           Show script version
    -u <user>           User to look up.
    -r <refresh_rate>   Refresh every <refresh_rate> seconds.

"""
from docopt import docopt
from time import sleep
from xolnowplaying.scrobbler import Scrobbler


class XolNowPlaying:

    def __init__(self, user):
        self.filename = 'xolnowplaying.txt'
        self.refresh(user)

    def refresh(self, user):
        self.scrobbler = Scrobbler(user)

    def run(self):
        string = ''
        if self.is_playing:
            string = '%s - %s' % (self.artist, self.title)
            if self.write_to_file(self.filename, string):
                Scrobbler.log('info ', string)
        else:
            string = ''
            self.write_to_file(self.filename, string)

    def write_to_file(self, filename, string):
        with open(filename, 'r') as f:
            read = f.readline()
        f.close()
        if not read == string:
            with open(filename, 'w') as f:
                try:
                    f.write(string)
                except UnicodeEncodeError:
                    pass
            f.close()
            return True
        else:
            return False

    def main(self, arguments):
        if not arguments['-r']:
            self.run()
        else:
            Scrobbler.log('debug', 'Refreshing every %s seconds' % (arguments['-r']))
            while True:
                self.run()
                sleep(float(arguments['-r']))
                self.refresh(arguments['-u'])
        return 0

    @property
    def is_playing(self):
        return self.scrobbler.np or False

    @property
    def artist(self):
        return self.scrobbler.artist or None

    @property
    def title(self):
        return self.scrobbler.title or None


if __name__ == '__main__':
    arguments = docopt(__doc__, version='xolnowplaying v0.1.2')
    np = XolNowPlaying(arguments['-u'])
    exit(np.main(arguments))
