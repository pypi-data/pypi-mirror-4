from datetime import datetime
import os,time,calendar

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
import pytz

from fa.apps import FoneAstraApp


register = template.Library()


@register.assignment_tag
def find_all_fa_apps():
    return ((reverse(app.app_index), app.app_name) for app
        in FoneAstraApp.find_all_fa_apps())
        

@register.filter
def to_js_timestamp(value):
    try:
        #Use this conversion if using the flot graphs.  It needs the
        #Flot graphs expect milliseconds since the epoch in local.
        return int(calendar.timegm(value.timetuple())*1000)
    except AttributeError:
        return ''


@register.filter
def to_string(value):
    return '\'%(value)s\'' % {'value': value}
