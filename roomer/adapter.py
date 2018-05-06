from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from roomer import settings
from django.utils import timezone

class DreamjubAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        print("IS OPEN FOR SIGNUP")
        print(sociallogin.account.extra_data)
        return super().is_open_for_signup(request, sociallogin)

    def populate_user(self, request, sociallogin, data):
        # TODO Populate users from sociallogin.account.extra_data
        print("POPULATE USER")
        print(sociallogin.account.extra_data)
        
        extra = sociallogin.account.extra_data
        user = sociallogin.user

        user.year = extra['year']
        user.major = extra['majorShort']
        user.country = extra['country']
        user.old_college = extra['college'] or ''

        user.housing_type = 0 # settings.HOUSING_TYPE_UNKNOWN

        # Subtract 2000 to make 2 digit years
        # This would normally be a stupid idea,
        # but Jacobs didn't exist before 2000,
        # so it's fine.
        year_now = timezone.now().year - 2000

        if extra['status'] == 'foundation-year':
            user.housing_type = 2 # settings.HOUSING_TYPE_FOUNDATION_YEAR
        elif extra['status'] == 'master':
            user.housing_type = max(6, min(7, extra['year'] - year_now + 6)) # settings.HOUSING_TYPE_MS_(1|2)
        elif extra['status'] == 'undergrad':
            user.housing_type = max(3, min(5, extra['year'] - year_now + 3)) # settings.HOUSING_TYPE_UG_(1|2|3)

        return super().populate_user(request, sociallogin, data)