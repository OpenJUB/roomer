from django import forms
from django.utils import timezone

from allocation.models import RoomPhase
from roomer.models import Room, College


class RoomPrefForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user_session = kwargs.pop('user', None)
        self.room_code = forms.CharField(label="Room choice:")

        super(RoomPrefForm, self).__init__(*args, **kwargs)

        self.fields['room_code'] = self.room_code

    def clean(self):
        cleaned_data = super(RoomPrefForm, self).clean()

        current_phase = RoomPhase.objects.get_current()

        if self.user_session is None:
            raise forms.ValidationError('You must be signed in to submit a room choice.')

        if current_phase is None:
            raise forms.ValidationError('No room allocation is currently being done.')

        if not current_phase.is_open():
            raise forms.ValidationError('This phase is not open at the moment.')

        # Check user eligible for phase
        (eligible, errors) = current_phase.is_user_eligible(self.user_session)

        if not eligible:
            raise forms.ValidationError(['You are not eligible for this phase for the following reasons:'] + errors)

        try:
            room = Room.objects.get(code=cleaned_data.get('room_code'))
        except Room.DoesNotExist:
            raise forms.ValidationError('The given room does not exist.')

        if room.college != self.user_session.college:
            raise forms.ValidationError('This room is not in your college.')

        (alloc, msg) = current_phase.is_allocating_room(room)

        if not alloc:
            raise forms.ValidationError(msg)

        self.cleaned_data = cleaned_data

