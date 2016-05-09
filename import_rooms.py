import json

from django.conf import settings
settings.configure()

from roomer.models import get_college_code

with open('old_rooms.json') as f:
    rooms = json.load(f)

    pk = 1

    name_to_ids = {}

    for room in rooms:
        if 'name' in room:
            name_to_ids[room['name']] = pk
            pk += 1

    room_objs = []

    for room in rooms[:50]:
        if 'name' in room:
            name = room['name']

            associated = []

            for other_room in rooms['rooms']:
                if 'name' in other_room and other_room['name'] != name:
                    associated.append(name_to_ids[other_room['name']])

            new_room = {
                'model': 'roomer.room',
                'pk': name_to_ids[name],
                'fields': {
                    'code': name,
                    'college': get_college_code(room['college']),
                    'floor': room['floor'],
                    'block': room['block'],
                    'associated': associated,
                }
            }

            room_objs.append(new_room)

    with open('room.json') as g:
        json.dumps(g, room_objs)