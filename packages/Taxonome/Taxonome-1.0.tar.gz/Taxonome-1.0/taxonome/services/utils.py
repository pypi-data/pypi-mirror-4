import urllib.request

from taxonome.config import config

USER_AGENT = config['main']['user-agent']

def urlopen(url, data=None):
    req = urllib.request.Request(url, data, headers={'ua': USER_AGENT})
    return urllib.request.urlopen(req)
