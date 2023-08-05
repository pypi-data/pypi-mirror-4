import logging, logging.handlers
import threading

from django.db import models
from django.conf import settings

from fa.transports.base import TransportBase
from fa.utils import regex_test


class FoneAstraDevice(models.Model):
    """
    Representation of a FoneAstra device.  All devices in FoneAstra apps should
    subclass this class.
    """

    class Meta:
        abstract = True
        unique_together = ('transport', 'name')

    # YES I KNOW HOW UN-DJANGONIC THIS IS.
    TRANSPORT_CHOICES = [(x.name, x.name) for x in TransportBase.get_all()]

    # The name of this device.
    name = models.CharField(blank=True, max_length=200)

    # The phone number of this device.
    phone_number = models.CharField(max_length=25)

    # The transport to use to talk to this device.
    transport = models.CharField(blank=True, null=True, max_length=255,
        choices=TRANSPORT_CHOICES)

    # The receivers for this device.  A tuple of tuples, where each inner tuple
    # contains a regex and a function.
    # Example: receivers = (
    #              (handlera.pattern, handlera.func),
    #              (handlerb.pattern, handlerb.func),
    #          )
    # Receivers are called with the following arguments:
    #   device - the FoneAstra device
    #   send_time - the time the message was sent
    #   *args - the matching groups of the pattern.
    receivers = ()

    def __unicode__(self):
        return "{cls}: {name}".format(
            cls=str(self.__class__.__name__),
            name=self.name,
        )

    def receive(self, msg):
        """
        This is called when a message is received from this device.

        Arguments:
            msg - the IncomingMessage corresponding to this device

        """
        func, match = regex_test(self.receivers, msg.content)
        if func:
            return func(self, msg.send_time, *match.groups())
        return False

    def send(self, message):
        """
        Sends the given message to this FoneAstra device using this device's
        configured transport. Returns True if the message was sent successfully,
        but makes no guarantees that it was received.

        Arguments:
            message - string
        """
        msg = OutgoingMessage(
            target = self.phone_number,
            content = message,
            transport = self.transport,
        )
        TransportBase.send(msg)


class IncomingMessage(models.Model):
    """
    Representation of an incoming message, such as that from a device.
    """

    sender = models.CharField(max_length=25)

    content = models.CharField(max_length=255)

    send_time = models.DateTimeField()

    transport = models.CharField(max_length=255)

    def __unicode__(self):
        return ("{sender}: {content} !@ {send_time}".format(
            sender=self.sender,
            content=self.content,
            send_time=self.send_time
        ))


class OutgoingMessage(models.Model):
    """
    Representation of an outgoing message, such as an alarm.
    """

    target = models.CharField(max_length=20)

    content = models.CharField(max_length=255)

    transport = models.CharField(max_length=255)

    def __unicode__(self):
        return ("{target}: {content}".format(
            target=self.target,
            content=self.content,
        ))
