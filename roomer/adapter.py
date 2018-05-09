from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from roomer import settings
from django.utils import timezone

from .utils import get_college_code

class DreamjubAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        #Fullname concatenated through jacobs API
        #Compared to the eligible_students.csv students
        fullname = sociallogin.account.extra_data.get('firstName') + ' ' + sociallogin.account.extra_data.get('lastName')
        if fullname not in settings.eligible_people:
            print("Fullname check failed: '{}'".format(fullname))
            return False
        return super().is_open_for_signup(request, sociallogin) and sociallogin.account.extra_data.get('active', False)

    def populate_user(self, request, sociallogin, data):
        extra = sociallogin.account.extra_data
        user = sociallogin.user

        user.year = extra['year']
        user.major = extra['majorShort']
        user.country = extra['country']
        user.old_college = get_college_code(extra['college'] or '')

        user.housing_type = 0 # settings.HOUSING_TYPE_UNKNOWN

        # Subtract 2000 to make 2 digit years
        # This would normally be a stupid idea,
        # but Jacobs didn't exist before 2000,
        # so it's fine.
        year_now = timezone.now().year - 2000

        if extra['status'] == 'foundation-year' or extra['status'] == 'medprep':
            user.housing_type = 2 # settings.HOUSING_TYPE_FOUNDATION_YEAR
        elif extra['status'] == 'master': #No more grads
            user.housing_type = max(6, min(7, 7 - abs(extra['year'] - year_now))) # settings.HOUSING_TYPE_MS_(1|2)
        elif extra['status'] == 'undergrad':
            user.housing_type = max(3, min(5, 5 - abs(extra['year'] - year_now))) # settings.HOUSING_TYPE_UG_(1|2|3)

        return super().populate_user(request, sociallogin, data)
