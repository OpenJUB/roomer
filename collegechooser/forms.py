from django.conf import settings
from django import forms


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