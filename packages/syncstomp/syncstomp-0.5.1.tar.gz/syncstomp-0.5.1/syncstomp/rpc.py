"""
Infrastructure for making Python classes that provide RPC over STOMP.
"""

import logging
logger = logging.getLogger(__name__)
from .conversation import SynchronousStomp, SynchronousStompErrorCode, repack_exception
from functools import wraps

RPC_METHOD_PREFIX = 'rpc_'
RPC_EXTENDED_METHOD_SUFFIX = '_ext'

def onecall(func):
    """Wrap a method call as a call-and-return RPC dialogue, such that the
       conversation object does not need to be passed to the method"""

    # For compatibility: if the function has been run through onecall already,
    # just return it
    if hasattr(func, 'wrapped'):
        return func

    @wraps(func)
    def wrapper(*args, **kwargs):
        conversation = kwargs.pop('conversation')
        logger.debug('%s(*%r, **%r)' % (func.func_name, args, kwargs))
        try:
            result = func(*args, **kwargs)
        except Exception as exc:
            logger.error('caught RPC exception', exc_info=True)
            conversation.error(SynchronousStompErrorCode.EXCEPTION,
                               repack_exception(exc))
            return
        conversation.reply(result, final=True)

    wrapper.wrapped = True
    return wrapper

class RpcProvider(SynchronousStomp):
    """An object offering services over RPC."""
    def __init__(self, stomp_connection, name=None, **kwargs):
        """Construct an RpcProvider.  This class must be subclassed, and the
           constructor must prepare a self.services dictionary mapping RPC verbs
           to functions that accept at least a 'conversation' parameter."""
        # Configure the underlying conversation engine
        SynchronousStomp.__init__(self,
            stomp_connection=stomp_connection,
            **kwargs)

        # Initialize the service directory, including automatically scanning
        # for methods that begin with 'rpc_'
        self.services = {'.list_services': self._rpc_list_services}
        for method_name in dir(self):
            if method_name.startswith(RPC_METHOD_PREFIX):
                service_name = method_name[len(RPC_METHOD_PREFIX):]
                if method_name.endswith(RPC_EXTENDED_METHOD_SUFFIX):
                    service_name = service_name[:-len(RPC_EXTENDED_METHOD_SUFFIX)]
                    method_func = getattr(self, method_name)
                else:
                    method_func = onecall(getattr(self, method_name))
                self.services[service_name] = method_func
        logger.info(self.services.keys())

        # Save parameters
        self.keep_running = True

        # Build a provider name if none given
        self.name = name or (self.__class__.__module__ + '.' +
                self.__class__.__name__)

    @onecall
    def _rpc_list_services(self):
        """(rpc method) Report the list of RPC services offered by this
           provider"""
        return {'services':     self.services.keys(),
                'services_doc': dict(((k, v.__doc__) for k, v in
                                      self.services.items())),
               }

    def on_unsolicited(self, message, conversation):
        """Handle incoming RPC requests"""

        # Make sure the request is constructed properly
        try:
            verb = message['verb']
            args = message['args']
            kwargs = message['kwargs']
        except KeyError:
            conversation.error(SynchronousStompErrorCode.BAD_MESSAGE,
                'Malformed RPC request')
            return

        try:
            func = self.services[verb]
        except KeyError:
            conversation.error(SynchronousStompErrorCode.BAD_MESSAGE,
                'RPC verb unknown')
            return

        # Perform the operation
        logger.debug('about to serve: %s(*%r, **%r) with %r'
                     % (verb, args, kwargs, func))
        func(*args, conversation=conversation, **kwargs)

class RpcProxy(object):
    """An RPC proxy object."""
    def __init__(self, rpc_destination, s_stomp):
        """Initialize an RpcProxy with an remote RpcProvider at rpc_destination
           through a SynchronousStomp object (s_stomp)."""
        self._rpc_destination = rpc_destination
        self._s_stomp = s_stomp
        self._services = {}
        self._update_services()

    def _update_doc(self, doc):
        """Update the proxy's internal representation of the object
           documentation."""
        self.__doc__ = doc

    def _build_rpc_request(self, verb, *args, **kwargs):
        """Construct an RPC request for execution"""
        return {'verb': verb, 'args': args, 'kwargs': kwargs}

    def _update_services(self):
        """Update the proxy's internal representation of the services offered by
           the RpcProvider"""
        conv = self._make_conversation()
        msg = self._build_rpc_request('.list_services')
        reply = conv.reply(msg)

        # Store the new representation
        self._services = reply['services']
        self._docs = reply['services_doc']

    def _make_conversation(self):
        """Construct and return a new conversation with the RPC Provider"""
        return self._s_stomp.solicit(self._rpc_destination)

    def __getattr__(self, name):
        """Return a wrapped proxy of an RpcProvider's service.  If the method
           name ends in _ext, then the returned value is a generator to which
           values may be sent (through the send() method) as replies to the
           conversation parter method."""
        # Prepare a wrapper
        if name.endswith('_ext'):
            name = name[:-4]

            # Attempting to access a nonexistant service is an error
            if name not in self._services:
                logger.error('service %s unknown' % name)
                raise AttributeError

            def method_wrap(*args, **kwargs):
                conv = self._make_conversation()
                msg = self._build_rpc_request(name, *args, **kwargs)
                try:
                    while not conv.ended:
                        msg = yield conv.reply(msg)
                except GeneratorExit:
                    if not conv.ended:
                        conv.reply(None, final=True)
        else:
            # Attempting to access a nonexistant service is an error
            if name not in self._services:
                logger.error('service %s unknown' % name)
                raise AttributeError

            def method_wrap(*args, **kwargs):
                conv = self._make_conversation()
                msg = self._build_rpc_request(name, *args, **kwargs)
                return conv.reply(msg)
        method_wrap.__doc__ = self._docs.get(name, '')
        method_wrap.func_name = name

        return method_wrap
