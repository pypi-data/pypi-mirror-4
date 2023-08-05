from .json_wrap import Connection
from stomp.utils import merge_headers

import logging
logger = logging.getLogger(__name__)

class DisconnectListener(object):
    def __init__(self, connection):
        self.connection = connection

    def on_disconnected(self):
        self.connection._disconnected()

    def on_connected(self, headers, body):
        self.connection._connected()

    def on_message(self, headers, message):
        pass

class ManagedConnection(Connection):
    """A self-reconnecting and re-subscribing STOMP connection"""
    def __init__(self, *args, **kwargs):
        # Create the subscription record
        self.subscriptions = {}

        # Initialize superclass
        super(ManagedConnection, self).__init__(*args, **kwargs)

        # Register listener
        self.set_listener('_managed', DisconnectListener(self))

        # Actually connect
        Connection.start(self)
        Connection.connect(self, wait=True)

    def start(self):
        pass

    def connect(self, wait=True):
        pass

    def subscribe(self, headers={}, **keyword_headers):
        # Determine the key parameters for resubscription
        hdr = merge_headers([headers, keyword_headers])

        assert 'destination' in hdr, "A subscription requires a destination."
        assert 'id' in hdr, "A ManagedConnection requires that every subscription have an ID."

        # Record the subscription
        self.subscriptions[hdr['id']] = hdr

        # The superclass method should fail if the subscription is invalid
        super(ManagedConnection, self).subscribe(headers=hdr)

    def unsubscribe(self, headers={}, **keyword_headers):
        # Determine the key parameters for resubscription
        hdr = merge_headers([headers, keyword_headers])

        assert 'id' in hdr, "An unsubscription requires an ID."

        # Remove the subscription
        if hdr['id'] in self.subscriptions:
            self.subscriptions.pop(hdr['id'])

        # The superclass method should fail if the subscription is invalid
        super(ManagedConnection, self).unsubscribe(headers=hdr)

    def _disconnected(self):
        # Attempt a reconnection
        logger.info('Disconnected from STOMP server.  Attempting reconnect.')
        self.start()
        self.connect(wait=True)

    def _connected(self):
        # Restore subscriptions
        logger.info('Connected to STOMP server.  Restoring subscriptions.')
        for hdr in self.subscriptions.values():
            super(ManagedConnection, self).subscribe(headers=hdr)
