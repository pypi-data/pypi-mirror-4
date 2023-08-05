from django.conf.urls.defaults import *

import fa.views as views

urlpatterns = patterns('',
    (r'^login$', 'django.contrib.auth.views.login', {'template_name': 'fa/login.html'}),
    (r'^logout$', 'django.contrib.auth.views.logout', {'template_name': 'fa/logout.html'}),
    url(r'^smssync$', views.smssync),
)
