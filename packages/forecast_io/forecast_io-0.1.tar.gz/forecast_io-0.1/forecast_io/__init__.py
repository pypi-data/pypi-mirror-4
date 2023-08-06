import json
import datetime
from requests import get
from requests.exceptions import RequestException

__all__ = [
    'AttrDict',
    'Forecast',
]

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, dict.__repr__(self))


class Forecast(object):

    def __init__(self, key):
        self._base_url = 'https://api.forecast.io/forecast'
        self._key = key

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._key)

    @property
    def _url(self):
        return '%s/%s' % (self._base_url, self._key)

    def forecast(self, latitude, longitude,
                 units='us', time=None, use_dicts=False):
        if isinstance(time, datetime.datetime):
            time = time.strftime('%s')
            args = locals()
            data = '%(latitude).4f,%(longitude).4f,%(time)s?units=%(units)s'
        else:
            args = locals()
            data = '%(latitude).4f,%(longitude).4f?units=%(units)s'
        url = '%s/%s' % (self._url, data % args)
        try:
            result = get(url, verify=False)
            if 'Forbidden' in result.content:
                raise Exception("invalid Dark Sky API key: %s" % self._key)
            result = json.loads(result.text,
                                object_hook=dict if use_dicts else AttrDict)
        except (TypeError, ValueError, RequestException):
            raise Exception("can't get data from forecast.io")
        return result


