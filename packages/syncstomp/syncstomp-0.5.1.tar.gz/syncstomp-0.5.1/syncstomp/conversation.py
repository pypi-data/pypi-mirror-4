from gevent.event import AsyncResult
from gevent import Timeout, spawn
from traceback import format_exc

import logging
logger = logging.getLogger(__name__)

class SynchronousStompException(Exception):
    pass

class OutOfSequenceReply(SynchronousStompException):
    pass

class RemoteException(Exception):
    def __init__(self, err_code, message='', origin=None, trace=None):
        self.err_code = err_code
        self.message = str(message)
        self.origin = origin
        self.trace = trace

    @classmethod
    def from_json(cls, err_code, msg):
        if err_code is not SynchronousStompErrorCode.EXCEPTION:
            return cls(err_code, msg, trace=[format_exc()])

        exc = cls(err_code,
                  message=msg['message'],
                  trace=msg['trace'],
                 )
        return exc

    def to_json(self):
        return {'message': self.message,
                'origin': self.origin,
                'trace': self.trace,
               }

    def __str__(self):
        return ('RemoteException(%s, "%s")\n%s\n%s'
                % (self.err_code,
                   self.message,
                   self.origin or '',
                   '\n'.join(self.trace or [])))

def repack_exception(exc):
    if isinstance(exc, RemoteException):
        trace = exc.trace or []
        trace.insert(0, format_exc())
        msg = exc.to_json()
        msg['trace'] = trace
    else:
        msg = {'message': exc.message,
               'origin': str(exc),
               'trace': [format_exc()],
              }
    return msg

class SynchronousStompErrorCode(object):
    TIMEOUT = 'TIMEOUT'
    BAD_MESSAGE = 'BAD_MESSAGE'
    EXCEPTION = 'EXCEPTION'

class Conversation(object):
    """The embodiment of a synchronous STOMP conversation.
       This class should only be constructed by SynchronousStomp."""

    def __init__(self, local_id, remote_id, reply_to, s_stomp):
        """Initialize a new conversation with a remote STOMP server."""
        self.s_stomp = s_stomp
        self.reply_to = reply_to
        self.local_id = local_id
        self.remote_id = remote_id
        self.async_result = None
        self.async_err = None
        self.ended = False

    def _message(self, message, reply_to=None, src_conv=None):
        """Handle an inbound conversation message"""
        # Make sure there is an async result waiting for an answer
        if self.async_result is None:
            logger.error('Unexpected message for conversation %s:%s' %
                (self.local_id, self.remote_id))
            return

        # Record the remote ID
        self.remote_id = src_conv

        # Detect conversation termination
        if reply_to is None:
            logger.debug('Received conversation termination for %s:%s with %s'
                         % (self.local_id, self.remote_id, repr(self.reply_to)))
            self.ended = True

        # Set the subsequent reply address
        self.reply_to = reply_to

        # Report the message
        async_result = self.async_result
        self.async_result = None
        async_result.set(message)

    def _error(self, exc):
        """Handle an inbound exception message"""
        # Make sure there is an async result waiting for an answer
        if self.async_result is not None:
            self.async_result.set_exception(exc)
        elif self.async_err is None:
            self.async_err = exc
        else:
            logger.critical('Dropping excess exception for %s:%s (%s)'
                            % (self.local_id, self.remote_id, exc))

    def _build_headers(self):
        headers = {'src-conversation': self.local_id}
        if self.async_result is not None:
            headers['reply-to'] = self.s_stomp.destination
        if self.remote_id is not None:
            headers['dst-conversation'] = self.remote_id
        return headers

    def reply(self, message, final=False, timeout=None):
        """Send a message to the conversation partner and wait for a response"""
        # Make sure this conversation participant hasn't aleady sent a reply
        if self.async_result is not None:
            logger.error('Out-of-sequence reply')
            raise OutOfSequenceReply

        # Treat as final if an error was recorded
        if self.async_err is not None:
            final = True

        # Prepare to receive a reply
        if not final:
            self.async_result = AsyncResult()
        else:
            # Cancel registration with the SynchronousStomp object
            self.s_stomp.convs.pop(self.local_id)

            # Recognize that the conversation has ended
            self.ended = True
            logger.debug('Ending conversation %s:%s with %s'
                         % (self.local_id, self.remote_id, self.reply_to))

        # Abort on error
        if self.async_err is not None:
            raise self.async_err

        # Build headers
        headers = self._build_headers()

        # Transmit message
        self.s_stomp.stomp.send(message,
                                destination=self.reply_to,
                                **headers)

        # Wait for a reply
        try:
            if not final:
                return self.async_result.get(timeout=timeout)
        except Timeout:
            self.error(SynchronousStompErrorCode.TIMEOUT)
            raise

    def error(self, err_code, message=''):
        """Transmit a message to the conversation partner"""
        # Build headers
        headers = self._build_headers()
        headers['SynchronousStomp-error'] = err_code
        logger.error('Sending conversation error message %s: %s' % (err_code, message))
        self.s_stomp.stomp.send(message, destination=self.reply_to, **headers)

class SynchronousStomp(object):
    """A wrapper around syncstomp for permitting synchronous conversations over STOMP"""
    SYNCHRONOUS_STOMP_COUNT = 0

    def __init__(self, stomp_connection, destination=None):
        # Record parameters
        self.stomp = stomp_connection
        self.destination = destination
        self.sync_id = '%s.SynchronousStomp_%d' % (__name__, SynchronousStomp.SYNCHRONOUS_STOMP_COUNT)
        SynchronousStomp.SYNCHRONOUS_STOMP_COUNT += 1

        # Initialize the conversation store
        self.conv_id = 0
        self.convs = {}

        # Calculate a unique destination if none was provided
        if self.destination is None:
            self.destination = '/temp-topic/%s' % self.sync_id

        # Register listener and subscribe
        self.stomp.set_listener(self.sync_id, self)
        self.stomp.subscribe(destination=self.destination, id=self.sync_id)

    def on_message(self, headers, message):
        """Handle an inbound synchronous STOMP message"""
        # Drop messages not intended for this subscription
        if headers['subscription'] != self.sync_id:
            return

        if 'src-conversation' not in headers:
            logger.error('%s: message missing source conversation id' % self.sync_id)
            return

        if 'dst-conversation' in headers:
            # Route messages to the proper thread
            conv_id = headers['dst-conversation']

            # Note the sender's conversation ID
            sender_id = headers['src-conversation']

            # Abort if convseration is unknown
            if conv_id not in self.convs:
                logger.error('%s: unknown conversation %s' % (self.sync_id, conv_id))
                return

            # Determine if the sender expects a reply
            reply_to = headers.get('reply-to', None)

            # Find the conversation in question
            conversation = self.convs[conv_id]

            # Determine if there was an exception
            if 'SynchronousStomp-error' in headers:
                # Build an exception
                err_code = headers['SynchronousStomp-error']
                exc = RemoteException.from_json(err_code, message)
                logger.error('%s: conversation %s error message: %s'
                             % (self.sync_id, conv_id, str(exc)))
                conversation._error(exc)

                # Abort regular handling
                return

            # Send the message to the conversation
            conversation._message(message, reply_to=reply_to, src_conv=sender_id)
        else:
            # Start a new conversation
            conv_id = str(self.conv_id)
            self.conv_id += 1
            conv = Conversation(local_id=conv_id,
                                remote_id=headers['src-conversation'],
                                reply_to=headers.get('reply-to', None),
                                s_stomp=self)
            self.convs[conv_id] = conv

            # Handle the unsolicited conversation
            spawn(self.on_unsolicited, message, conv)

    def on_unsolicited(self, message, conversation):
        """Handle an unsolicited message.  Should be overridden."""
        pass

    def solicit(self, destination):
        # Start a new conversation
        conv_id = str(self.conv_id)
        self.conv_id += 1
        conv = Conversation(local_id=conv_id,
                            remote_id=None,
                            reply_to=destination,
                            s_stomp=self)
        self.convs[conv_id] = conv
        return conv
