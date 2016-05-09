from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^$', overview, name='college-overview'),
]
