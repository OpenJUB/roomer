from django.conf import settings
from django import forms

from roomer.models import Room, College


class RoomField(forms.ChoiceField):
    def __init__(self, college, *args, **kwargs):
        if 'choices' in kwargs:
            del kwargs['choices']

        super(RoomField, self).__init__(*args,
                                        choices=Room.objects.filter(college=College.objects.filter(name=college)),
                                        **kwargs)


class RoomPrefForm(forms.Form):
    pref_1 = RoomField(label="Preference 1")
    pref_2 = RoomField(label="Preference 2")
    pref_3 = RoomField(label="Preference 3")
    pref_4 = RoomField(label="Preference 4")
    pref_5 = RoomField(label="Preference 5")
    pref_6 = RoomField(label="Preference 6")
    pref_7 = RoomField(label="Preference 7")

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

    def to_pref_string(self):
        return "{0}:{1}:{2}:{3}:{4}:{5}:{6}".format(
            self.cleaned_data.get('pref_1'),
            self.cleaned_data.get('pref_2'),
            self.cleaned_data.get('pref_3'),
            self.cleaned_data.get('pref_4'),
            self.cleaned_data.get('pref_5'),
            self.cleaned_data.get('pref_6'),
            self.cleaned_data.get('pref_7'),
        )

    @staticmethod
    def from_pref_string(pref_string):
        preferences = pref_string.split(":")
        if len(preferences) != 7:
            return RoomPrefForm()

        return RoomPrefForm(initial={
            'pref_1': preferences[0],
            'pref_2': preferences[1],
            'pref_3': preferences[2],
            'pref_4': preferences[3],
            'pref_5': preferences[4],
            'pref_6': preferences[5],
            'pref_7': preferences[6]
        })


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
