import inspect

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

class FoneAstraApp(object):
    """
    Core app that all FoneAstra apps should subclass.  Includes extra methods
    and fields for interfacing with FoneAstra, and FoneAstra autodiscovery
    only includes apps that subcless FoneAstraApp.

    """

    # The name of the app (string).
    app_name = None

    # The app's index view name (string).
    # Example: `app name`_index
    app_index = None

    # The class definitions of all FoneAstra devices in this app.
    device_types = ()

    # Used to lazily initialize the apps list.
    _apps = None

    @classmethod
    def find_all_fa_apps(cls):
        if cls._apps is not None:
            return cls._apps
        for app_name in settings.INSTALLED_APPS:
            try:
                __import__(app_name + ".app")
            except ImportError:
                pass
        cls._apps = [x for x in cls.__subclasses__()
            if inspect.getmodule(x).__package__ in settings.INSTALLED_APPS]
        return cls._apps

    @classmethod
    def get_device(cls, phone_number):
        """
        Returns the FoneAstra device corresponding to this project and
        phone number, or None if no such device exists.

        """
        for device_type in cls.device_types:
            try:
                return device_type.objects.get(phone_number=phone_number)
            except ObjectDoesNotExist:
                pass
        return None

    @classmethod
    def receive(cls, msg):
        """
        This method gets called if a message arrives that did not come from any
        registered FoneAstra device in any app.  This method is most frequently
        called for configuration messages.

        """
        pass
