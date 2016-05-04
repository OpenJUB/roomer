from django.contrib import admin
from roomer.models import UserProfile, RoommateRequest


class UserProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('points', 'year', 'major', 'country', 'old_college', 'seniority')
    model = UserProfile

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(RoommateRequest)