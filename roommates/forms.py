from django import forms
from django.contrib.auth import get_user_model


class RequestRoommateForm(forms.Form):
    receiver = forms.CharField()

    def __init__(self, *args, **kwargs):
            super(RequestRoommateForm, self).__init__(*args, **kwargs)
            self.fields['receiver'].error_messages = {'required': 'Enter the CampusNet username of your friend.'}

    def clean(self):
        cleaned_data = super(RequestRoommateForm, self).clean()

        user_model = get_user_model()

        try:
            user = user_model.objects.get(username=cleaned_data.get('receiver'))
        except user_model.DoesNotExist:
            raise forms.ValidationError(
                "This user does not exist. "
                "Maybe your friend just hasn't logged in yet."
            )

        self.cleaned_data = cleaned_data