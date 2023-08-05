from fa.transports.base import TransportBase

class Transport(TransportBase):
    """
    Transport for using an Android phone running SMSSync as the router.

    Configuration options:
        "secret" - SMSSync secret to use for device verification (no two SMSSync
                   transports running on the same server may have the same
                   secret)
    """


    def __init__(self, name, config):
        self.name = name
        self.config = config

    def _send(self, msg):
        """
        These messages get cleared in the HTTP thread, so just save them.

        """
        msg.save()
