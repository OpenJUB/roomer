from django.contrib.auth.forms import AuthenticationForm


class RoomerAuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(RoomerAuthForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "Campusnet username"