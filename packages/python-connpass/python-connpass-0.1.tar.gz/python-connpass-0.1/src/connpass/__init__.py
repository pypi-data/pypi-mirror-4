#
import json
import requests
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
from six import text_type


API_URL = 'http://connpass.com/api/v1/event/'

def maybe_encoded(s):
    if isinstance(s, text_type):
        return s.encode('utf-8')
    return s

class Connpass(object):
    def __init__(self, api_url=API_URL):
        self.api_url = api_url

    def search(self,
                 event_id=[],
                 keyword=[],
                 keyword_or=[],
                 ym=[],
                 ymd=[],
                 nickname=[],
                 owner_nickname=[],
                 series_id=[],
                 start=None,
                 count=None,
                 format='json'):
        __ = maybe_encoded

        params = (
            [("event_id", __(e)) for e in event_id]
            + [("keyword", __(k)) for k in keyword]
            + [("keyword_or", __(k)) for k in keyword_or]
            + [("ym", __(y)) for y in ym]
            + [("ymd", __(y)) for y in ymd]
            + [("nickname", __(n)) for n in nickname]
            + [("owner_nickname", __(o)) for o in owner_nickname]
            + [("series_id", __(s)) for s in series_id]
            + [("start", __(start)),
               ("count", __(count)),
               ("format", format),
           ])

        r = requests.get(self.api_url, params=urlencode(params))

        return json.loads(r.text)


def main():
    """ test access """

    from pprint import pprint
    connpass = Connpass()

    pprint(connpass.search(event_id=[364, 365]))
