#!/usr/bin/env python

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "roomer.settings")

from roomer.models import *
from .utils import *

def dry_run():
    i = InboxNotification(RoommateRequest.objects.first())
    i.send()