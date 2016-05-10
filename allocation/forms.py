from django.conf import settings
from django import forms

from roomer.models import Room, College


class RoomField(forms.ChoiceField):
    def __init__(self, college, *args, **kwargs):
        if 'choices' in kwargs:
            del kwargs['choices']

        super(RoomField, self).__init__(*args,
                                        choices=Room.rooms.get_by_college(college),
                                        **kwargs)


class RoomPrefForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        self.user_session = user
        self.pref_1 = RoomField(self.user_session.college, label="1st Preference")
        self.pref_2 = RoomField(self.user_session.college, label="2nd Preference")
        self.pref_3 = RoomField(self.user_session.college, label="3rd Preference")
        self.pref_4 = RoomField(self.user_session.college, label="4th Preference")
        self.pref_5 = RoomField(self.user_session.college, label="5th Preference")
        self.pref_6 = RoomField(self.user_session.college, label="6th Preference")
        self.pref_7 = RoomField(self.user_session.college, label="7th Preference")

        super(RoomPrefForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(RoomPrefForm, self).clean()
        preferences = [
            cleaned_data.get('pref_1'),
            cleaned_data.get('pref_2'),
            cleaned_data.get('pref_3'),
            cleaned_data.get('pref_4'),
            cleaned_data.get('pref_5'),
            cleaned_data.get('pref_6'),
            cleaned_data.get('pref_7')
        ]
        if any(preferences.count(x) > 1 for x in preferences):
            raise forms.ValidationError("You can't select the same room as two preferences")
        self.cleaned_data = cleaned_data


class CollegeField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        if 'choices' in kwargs:
            del kwargs['choices']

        super(CollegeField, self).__init__(*args, choices=settings.COLLEGE_CHOICES, **kwargs)


class CollegePrefForm(forms.Form):
    pref1 = CollegeField(label="Preference 1")
    pref2 = CollegeField(label="Preference 2")
    pref3 = CollegeField(label="Preference 3")
    pref4 = CollegeField(label="Preference 4")

    def clean(self):
        cleaned_data = super(CollegePrefForm, self).clean()

        prefs = [
            cleaned_data.get('pref1'),
            cleaned_data.get('pref2'),
            cleaned_data.get('pref3'),
            cleaned_data.get('pref4')
        ]

        # Check for dupes
        if any(prefs.count(x) > 1 for x in prefs):
            raise forms.ValidationError(
                "You can't select the same college as two preferences."
            )

        self.cleaned_data = cleaned_data

    def to_pref_string(self):
        return "{0}:{1}:{2}:{3}".format(
            self.cleaned_data.get('pref1'),
            self.cleaned_data.get('pref2'),
            self.cleaned_data.get('pref3'),
            self.cleaned_data.get('pref4')
        )

    @staticmethod
    def from_pref_string(pref_string):
        prefs = pref_string.split(":")

        if len(prefs) != 4:
            return CollegePrefForm()

        return CollegePrefForm(initial={
            'pref1': prefs[0],
            'pref2': prefs[1],
            'pref3': prefs[2],
            'pref4': prefs[3],
        })
