"""
KISSmetrics API client
======================

Example usage:

km = KM('my-api-key')
km.identify('simon')
km.record('an event', {'attr': '1'})

"""
import logging
from datetime import datetime

import pytool
import urllib3


@pytool.lang.hashed_singleton
class API(object):
    """ KISSmetrics API client class. """
    def __init__(self, api_key, host='trk.kissmetrics.com', http_timeout=2):
        # Handle port numbers gracefully
        if ':' in host:
            host, port = host.split(':')
            port = int(port)
        else:
            port = 80

        self._api_key = api_key
        self._http = urllib3.HTTPConnectionPool(host, port,
                timeout=http_timeout)

    def record(self, identity, action, props=None):
        """ Record `action` with the KISSmetrics API.

            :param str identity: User identity
            :param str action: Action to record
            :param dict props: Additional information to include

        """
        props = props or {}

        if isinstance(action, dict):
            self.set(action)

        props.update({'_n': action})
        return self.request('e', props, identity=identity)

    def set(self, identity, data):
        """ Set a data key.

            :param str identity: User identity
            :param dict data: Data to set

        """
        return self.request('s', data, identity=identity)

    def alias(self, name, alias_to):
        """ Create an identity alias.

            :param str name: Identity to alias
            :param str alias_to: New alias for identity

        """
        return self.request('a', {'_n': alias_to, '_p': name})

    def request(self, path, data, identity=None):
        """ Make HTTP request to KISSmetrics API.

            :param str path: Request path
            :param dict data: Data params

        """
        # if user has defined their own _t, then include necessary _d
        if '_t' in data:
            data['_d'] = 1
        else:
            data['_t'] = pytool.time.toutctimestamp(pytool.time.utcnow())

        # Add API key to data
        data['_k'] = self._api_key

        # Add identity to data
        if identity:
            data['_p'] = identity

        # Add leading / to path, not strictly necessary, but whatever
        path = '/{}'.format(path)
        try:
            response = self._http.request('GET', path, data)
            return response.status == 200
        except:
            logging.getLogger(__name__).error("Error with request.",
                    exc_info=True)
        return False


class KM(object):
    """ Wrapper around :class:`API` to match the original KISSmetrics API
        client.

    """
    def __init__(self, key, host='trk.kissmetrics.com:80', http_timeout=2,
            logging=False):
        self._id = None
        self._key = key
        self._host = host
        self._http_timeout = http_timeout
        self._logging = logging

    @property
    def api(self):
        """ Return an :class:`API` instance. """
        return API(self.key, self._host, self._http_timeout)

    def identify(self, id):
        self._id = id

    def record(self, action, props=None):
        """ Record `action` with the KISSmetrics API.

            :param str action: Action to record
            :param dict props: Additional information to include

        """
        props = props or {}
        self.check_id_key()

        if isinstance(action, dict):
            self.set(action)

        return self.api.record(self._id, action, props)

    def set(self, data):
        """ Set a data key.

            :param dict data: Data to set

        """
        self.check_id_key()
        return self.api.set(self._id, data)

    def alias(self, name, alias_to):
        """ Create an identity alias. """
        self.check_init()
        return self.api.alias(name, alias_to)

    def reset(self):
        """ Reset client instance, forgetting the identity and API key. """
        self._id = None
        self._key = None

    def check_identify(self):
        """ Check if we have an identity set. """
        if self._id is None:
            raise RuntimeError("Need to identify first (KM.identify('<user>'))")

    def check_init(self):
        """ Check if we have been initialized with an API key. """
        if self._key is None:
            raise RuntimeError("Need to initialize first (KM.init('<your_key>'))")

    def now(self):
        """ Return the current UTC time. """
        return datetime.utcnow()

    def check_id_key(self):
        """ Check that we have an `identity` and that the client has been
            properly initialized.

        """
        self.check_init()
        self.check_identify()

