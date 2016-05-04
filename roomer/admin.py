from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from roomer.models import UserProfile, RoommateRequest

admin.site.unregister(User)


class UserProfileInline(admin.StackedInline):
    readonly_fields = ('points', 'year', 'major', 'country', 'old_college', 'seniority')
    model = UserProfile


class UserProfileAdmin(UserAdmin):
    inlines = [UserProfileInline, ]

admin.site.register(User, UserProfileAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('points', 'year', 'major', 'country', 'old_college', 'seniority')
    model = UserProfile

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(RoommateRequest)