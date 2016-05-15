from django.conf.urls import url, include

from .views import *

urlpatterns = [
    url(r"^$", overview, name='roommate-overview'),

    url(r"^roommate/(?P<roommate_id>\d+)/", include(
        [
            url(r'^delete$', remove, name='roommate-remove'),
        ]
    )),

    url(r"^request/(?P<request_id>\d+)/", include(
        [
            url(r'^deny$', deny, name='request-deny'),
            url(r'^accept$', accept, name='request-accept'),
        ]
    )),

    url(r'^request/send$', invite, name='roommate-invite'),
    url(r'^request/freshie$', invite_freshman, name='roommate-freshman'),

    url(r'^autocomplete$', autocomplete, name='user-autocomplete')
]