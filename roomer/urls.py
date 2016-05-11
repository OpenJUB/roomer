"""roomer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from .views import home
from .forms import RoomerAuthForm

urlpatterns = [
    url(r'^$', home, name="home"),
    url(r'^admin/', admin.site.urls),

    # College allocation
    url(r'^colleges/', include('collegechooser.urls')),

    # Roommate system
    url(r'^roommates/', include('roommates.urls')),

    # Allocation system
    url(r'^allocation/', include('allocation.urls')),

    # Authentication
    url(r'^login/', auth_views.login, {'authentication_form': RoomerAuthForm, 'template_name': 'auth/login.html'}, name="login"),
    url(r'^logout/', auth_views.logout, {'template_name': 'auth/logout.html', 'next_page': 'home'}, name="logout"),
]
