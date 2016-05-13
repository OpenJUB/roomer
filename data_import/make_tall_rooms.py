#!/usr/bin/env python
__author__ = 'leonhard'

import json
import sys
import os
import django
from django.db.transaction import atomic

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "roomer.settings")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

django.setup()

from roomer.models import Room, RoomTag
from django.db.models import Q

import json

from pprint import pprint

# Krupp, Mercator

krme = Room.objects.filter(college__in=['KR', 'ME'])\
    .filter(Q(code__endswith='08') | Q(code__endswith='09') | Q(code__endswith='36') | Q(code__endswith='37')).exclude(block='D')


# NM

nm = Room.objects.filter(college='NM', block='B')\
    .filter(Q(code__endswith='80') |
            Q(code__endswith='81') |
            Q(code__endswith='84') |
            Q(code__endswith='85') |
            Q(code__endswith='88') |
            Q(code__endswith='89') |
            Q(code__endswith='92') |
            Q(code__endswith='93') |
            Q(code__endswith='96') |
            Q(code__endswith='97'))


# C3

c3 = Room.objects.filter(college='C3')\
    .filter(Q(code__endswith='08') | Q(code__endswith='09'))


tall_rooms = krme | nm | c3



for room in tall_rooms:
    RoomTag.objects.create(room=room, tag='tall', generated=False)



# with open('tall_rooms.json', 'w') as f:
#    json.dump(list(tall_rooms.order_by('code').values_list('code', flat=True)), f)