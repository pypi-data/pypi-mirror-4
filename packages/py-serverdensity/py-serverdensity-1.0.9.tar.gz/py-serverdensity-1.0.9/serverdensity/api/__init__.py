import os
import requests
try:
    import simplejson as json
except ImportError:
    import json


def get_version_string():
    return open(os.path.join(os.path.dirname(__file__),
                'version.txt'), 'r').read().strip()


def get_version():
    return get_version_string().split('.')

__version__ = get_version_string()


GETS = {
    'alerts': (
        'getHistory', 'getLast', 'getOpen', 'getOpenNotified', 'list',
    ),
    'services': (
        'list',
    ),
    'devices': (
        'getByGroup', 'getByHostName', 'getById', 'getByIp', 'getByName',
        'list', 'listGroups', 'count',
    ),
    'metrics': (
        'getLatest', 'getRange', 'list',
    ),
    'mongo': (
        'getMaster', 'getReplicaSet',
    ),
    'processes': (
        'getByTime', 'getRange',
    ),
    'users': (
        'getById', 'list',
    ),
}

POSTS = {
    'alerts': (
        'pause', 'resume', 'add', 'delete'
    ),
    'devices': (
        'add', 'addGroup', 'delete', 'rename', 'addAggregate', 'editAggregate',
    ),
    'metrics': (
        'postback',
    ),
    'users': (
        'add', 'delete', 'addPhone', 'addEmail', 'deletePhone', 'deleteEmail',
    ),
}

API_VERSION = '1.4'
BASE_URL = 'https://api.serverdensity.com/%(version)s/%(section)s/%(method)s'


class SDApi(object):
    """Lightweight ServerDensity.com API wrapper
    """
    def __init__(self, account, username, password, api_key=None, name=None,
                 gets=GETS, posts=POSTS, base_url=BASE_URL,
                 api_version=API_VERSION):
        self._account = account
        self._username = username
        self._password = password
        self._name = name
        self._gets = gets
        self._posts = posts
        self._base_url = base_url
        self._api_version = api_version

    def _request(self, method, data={}, params={}):
        if 'account' not in params:
            params['account'] = self._account

        url = self._base_url % {
            'version': self._api_version,
            'section': self._name,
            'method': method,
        }

        if self._name not in self._gets and self._name not in self._posts:
            raise AttributeError(u'No section named %s' % (self._name,))

        if method in self._gets[self._name]:
            params.update(data)
            request = requests.get(url, params=params, auth=(self._username,
                self._password))
        elif method in self._posts[self._name]:
            request = requests.post(url, data=data, params=params, auth=(
                                    self._username, self._password))
        else:
            raise AttributeError(u'No method named %s' % (method,))

        response = json.loads(request.content)
        if response['status'] == 2:
            raise SDServiceError(response['error']['message'],
                                 response=response)
        return response

    def __getattr__(self, attr_name):
        if self._name is None:
            return super(SDApi, self).__self_class__(
                account=self._account,
                username=self._username,
                password=self._password,
                name=attr_name
            )
        else:
            def wrapper(*args, **kwargs):
                return self._request(attr_name, *args, **kwargs)
            return wrapper


class SDServiceError(Exception):
    """Container for API errors from serverdensity.com
    """
    def __init__(self, *args, **kwargs):
        self.response = kwargs.get('response', {})

        if 'response' in kwargs:
            del kwargs['response']

        super(SDServiceError, self).__init__(*args, **kwargs)
