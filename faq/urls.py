from django.conf.urls import url
from .views import home, add

urlpatterns = [
    url(r'^$', home, name="question-home"),
    url(r'^add/', add, name="question-add"),
]
