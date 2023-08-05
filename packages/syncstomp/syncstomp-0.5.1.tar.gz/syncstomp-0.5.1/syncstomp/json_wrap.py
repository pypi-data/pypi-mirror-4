from stomp import Connection as RawConnection
from plumb_util import find_service
import json
import cPickle as pickle
from base64 import b64encode, b64decode

import logging
logger = logging.getLogger(__name__)

def on_exception_wrap(wrapper, name):
    def on_exception_wrapper(exc):
        logger.critical('caught %s exception: %s', name, exc, exc_info=True)
        if hasattr(wrapper, 'on_exception'):
            wrapper.on_exception(exc)
    return on_exception_wrapper

class _ListenerWrapper(object):
    def __init__(self, listener):
        self.listener = listener
    def __dir__(self):
        return dir(self.listener)
    def __getattr__(self, name):
        return getattr(self.listener, name)
    def on_send(self, headers, body):
        if 'on_send' in dir(self.listener):
            return self.listener.on_send(headers, body)
    def on_message(self, headers, json_message):
        # Determine the encoding (JSON by default)
        content_type = headers.get('content-type', 'application/json')

        # Find the decoder for the encoding
        if   content_type == 'application/json': decode = json.loads
        elif content_type == 'application/x-python-pickle': decode = pickle.loads
        elif content_type == 'application/x-python-pickle-b64': decode = lambda x: pickle.loads(b64decode(x))
        else: decode = lambda x: x

        # Attempt to parse message
        try:
            message = decode(json_message)
        except ValueError:
            logger.error('JSON parse error')
            if hasattr(self, 'on_parseerror'):
                self.on_parseerror(headers, json_message)
            return

        # Send on the message
        try:
            self.listener.on_message(headers, message)
        except Exception as exc:
            on_exception_wrap(self, 'on_message')(exc)

class Connection(RawConnection):
    """A json-wrapped version of stomp.py's Connection object with DNS service
       autodiscovery."""
    def __init__(self, zone=None, prefer_localhost=False, **kwargs):
        # Find the hosts
        host_and_ports = find_service('_stomp._tcp', zone=zone)

        # Initialize superclass
        super(Connection,self).__init__(host_and_ports=host_and_ports,
                                           prefer_localhost=prefer_localhost,
                                           **kwargs)

    def send(self, message={}, headers={}, content_type='application/json', **keyword_headers):
        """Send a message (SEND) frame with some encoding (usually JSON)"""
        # Determine the encoding
        content_type = headers.get('content-type', content_type)
        if 'content-type' not in headers:
            headers = headers.copy()
            headers['content-type'] = content_type

        # Encode according to the encoding
        if   content_type == 'application/json': encode = json.dumps
        elif content_type == 'application/x-python-pickle': encode = pickle.dumps
        elif content_type == 'application/x-python-pickle-b64': encode = lambda x: b64encode(pickle.dumps(x))
        else: encode = lambda x: x
        msg = encode(message)

        # Send message
        super(Connection,self).send(message=msg,
                                    headers=headers,
                                    **keyword_headers)

    def set_listener(self, name, listener):
        """Set a named listener on this connection.  Messages will be
           JSON-parsed"""
        super(Connection,self).set_listener(name, _ListenerWrapper(listener))
