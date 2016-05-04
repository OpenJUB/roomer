from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from roomer.models import UserProfile, RoommateRequest

admin.site.unregister(User)


class UserProfileInline(admin.StackedInline):
    model = UserProfile


class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline, ]

admin.site.register(User, UserAdmin)


admin.site.register(UserProfile)
admin.site.register(RoommateRequest)