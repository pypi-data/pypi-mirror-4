from collections import defaultdict
import logging

from django.conf import settings
from django.utils.importlib import import_module

from fa.apps import FoneAstraApp


logger = logging.getLogger(__name__)


class TransportBase(object):
    """
    Base class for all transports.  Defines methods that transports must
    implement.

    All Transport constructors must take the name of the transport (string) as
    their first argument, and they are passed the entire configuration dict
    (from the global settings file) as **kwargs.

    """

    # Lazily initialize our transports list.
    _transports = None

    @classmethod
    def get_transport(cls, name):
        """Gets a transport object from its configured name."""
        cls._generate_transports()
        if name not in cls._transports:
            raise NoTransportException("Could not find transport " + str(name))
        return cls._transports[name]
    
    @classmethod
    def get_all(cls):
        """Returns a list of all transports."""
        cls._generate_transports()
        return [b for a, b in cls._transports.items()]

    @classmethod
    def _generate_transports(cls):
        """Populates the _transports field."""
        if cls._transports is not None:
            return

        transports_local = {}
        for name, config in settings.TRANSPORTS.iteritems():
            transport_class = import_module(config["ENGINE"]).Transport
            transports_local[name] = transport_class(name, config)
            logger.debug("Adding transport {name}".format(name=name))
        cls._transports = transports_local

    @classmethod
    def receive(cls, msg):
        """
        Call this function to process an incoming message from a FoneAstra device.
        Returns true if an app or device handled the message, False otherwise.

        Arguments:
            msg - an IncomingMessage

        """
        
        # First check to see if this is a message from a registered device.
        for app in FoneAstraApp.find_all_fa_apps():
            device = app.get_device(msg.sender)
            if device:
                logger.info('Received message from FA device {name}: {content}'.format(
                    name=device.name,
                    content=msg.content,
                ))
                if msg.transport != device.transport:
                    logger.warning('Received message from FA device {name} on transport {transport} (expected {expected})'.format(
                        name=device.name,
                        transport=msg.transport,
                        expected=device.transport,
                    ))
                # If this returns false, it might be a config. Pass it on to the
                # apps.
                if device.receive(msg):
                    return True

        # If it's not a registered device, just have every app look at it in order.
        for app in FoneAstraApp.find_all_fa_apps():
            if app.receive(msg):
                logger.info('Message {content} from {sender} successfully processed by {app}'.format(
                    content=msg.content,
                    sender=msg.sender,
                    app=app.app_name,
                ))
                return True

        # None of the apps want it.
        logger.warning('Unprocessed message from {sender}: {content}'.format(
            sender=msg.sender,
            content=msg.content
        ))
        return False

    @classmethod
    def send(cls, msg):
        """
        Sends a single message consisting of "content" to the target.

        Arguments:
            msg - OutgoingMessage

        """
        transport = cls.get_transport(msg.transport)
        transport._send(msg)

    @classmethod
    def send_batch(self, lst):
        """
        Sends all of the messages in lst, since some transports have more
        efficient options for batch sending.

        Arguments:
            lst - a list of OutgoingMessages

        """
        messages = defaultdict(list)
        for msg in lst:
            messages[msg.transport].append(msg)
        for transport_name, msg_list in messages.iteritems():
            transport = cls.get_transport(transport_name)
            transport._send_batch(msg_list)

    def _send(self, msg):
        """
        Private method to hand the actual sending.

        """
        pass

    def _send_batch(self, lst):
        """
        Private method to handle the actual batch sending.

        """
        for msg in lst:
            self._send(msg)

class NoTransportException(Exception):
    """Raised when attempting to send a message with an invalid transport."""
    def __init__(self, value=""):
        self.value=value
    def __str__(self):
        return repr(self.value)
