import json
import os

COLLEGE_CHOICES = [
    ('NM', 'Nordmetall'),
    ('C3', 'C3'),
    ('KR', 'Krupp'),
    ('ME', 'Mercator')
]


def get_college_code(college_str):
    for college in COLLEGE_CHOICES:
        if college[1] == college_str:
            return college[0]
    return ''

with open('old_rooms.json') as f:
    rooms = json.load(f)

    pk = 1

    name_to_ids = {}

    for room in rooms:
        if 'name' in room:
            name_to_ids[room['name']] = pk
            pk += 1

    room_objs = []

    for room in rooms:
        if 'name' in room:
            name = room['name']

            associated = []

            for other_room in room['rooms']:
                if other_room != name:
                    try:
                        associated.append(name_to_ids[other_room])
                    except KeyError:
                        print("Couldn't find associated room " + other_room + ".")

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

    with open('rooms.json', 'w') as g:
        json.dump(room_objs, g)
