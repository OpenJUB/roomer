from django.conf.urls import url, include

from .views import *

urlpatterns = [
    url(r'^$', list_preferences, name='room-request-overview'),
    url(r'results$', room_results, name='room-results'),

    url(r'^request/(?P<pref_id>\d+)/', include(
        [
            url(r'^remove$', remove_preference, name='room-request-remove'),
            url(r'^up$', preference_up, name='room-request-up'),
            url(r'^down$', preference_down, name='room-request-down'),
        ]
    )),

    #url(r'^apply$', apply_for_room, name='room-request-send'),
    url(r'^autocomplete$', room_code_autocomplete, name='room-code-autocomplete'),
    url(r'^swap$', swap_rooms, name='swap-rooms'),
]
