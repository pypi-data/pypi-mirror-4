import collections
from datetime import datetime
import logging
import re
import sys

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import simplejson
from django.utils.timezone import get_default_timezone
from django.views.decorators.csrf import csrf_exempt

from fa.apps import FoneAstraApp
from fa.models import IncomingMessage, OutgoingMessage
from fa.transports.base import TransportBase, NoTransportException
from fa.transports.smssync import Transport


logger = logging.getLogger(__name__)


@login_required
def index(req):
    apps = FoneAstraApp.find_all_fa_apps()
    if len(apps) == 1:
        return redirect(apps[0].app_index)
    return render(req, "fa/index.html")

@csrf_exempt
def smssync(request):
    if 'secret' not in request.REQUEST:
        if settings.DEBUG:
            return HttpResponse(simplejson.dumps(_debug()), mimetype="application/json")
        else:
            return HttpResponse("Debug mode currently disabled.")
    with transaction.commit_on_success():
        payload = {
            'secret': request.REQUEST['secret'],
        }
        transport = find_transport(payload['secret'])

        if request.method == 'POST':
            sender = request.POST['from']
            content = request.POST['message']

            # See that whole "hour = blah % 24" thing?  We need to handle
            # all of this weird regex stuff instead of just using strptime
            # because SMSSync returns times between midnight and one as
            # 24:XX, not 00:XX.
            matches = re.match(
                "(\d+)-(\d+)-(\d+) (\d+):(\d+)",
                request.POST['sent_timestamp'],
            )
            month = int(matches.group(1))
            day = int(matches.group(2))
            year = int(matches.group(3)) + 2000
            hour = int(matches.group(4)) % 24
            minute = int(matches.group(5))

            send_time = datetime(year, month, day, hour, minute).replace(
                tzinfo=get_default_timezone()
            )
            message = IncomingMessage(
                transport=transport.name,
                sender=sender,
                content=content,
                send_time=send_time,
            )
            payload['success'] = ("true" if TransportBase.receive(message) else "false")

        outgoing_messages = OutgoingMessage.objects.filter(
            transport=transport.name
        )
        if len(outgoing_messages) > 0:
            payload['task'] = "send"
            messages = [{
                "to": msg.target,
                "message": msg.content,
            } for msg in outgoing_messages]

            # Don't delete if we're viewing this in a browser.
            if ('HTTP_USER_AGENT' not in request.META
                    or 'SMSSync' in request.META['HTTP_USER_AGENT']):
                outgoing_messages.delete()
            payload['messages'] = messages

        reply = {
            "payload": payload
        }
        return HttpResponse(simplejson.dumps(reply), mimetype="application/json")

def find_transport(secret):
    """
    Finds the SMSSync transport with the given secret.  Throws an exception if
    if it cannot find one.

    """
    for transport in TransportBase.get_all():
        if isinstance(transport, Transport):
            if transport.config['secret'] == secret:
                return transport
    raise NoTransportException()


def _debug():
    """
    Returns debugging information in the form of of a dict mapping SMSSync
    secrets to list of all messages using that transport.

    """
    messages = collections.defaultdict(list)
    for msg in OutgoingMessage.objects.all():
        messages[msg.transport].append(str(msg))
    return messages
