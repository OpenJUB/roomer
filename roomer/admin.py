from django.contrib import admin
from roomer.models import UserProfile, RoommateRequest, Room, RoomTag, College


class UserProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('points', 'year', 'major', 'country', 'old_college', 'seniority')
    model = UserProfile

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(RoommateRequest)


class TagInline(admin.TabularInline):
    model = RoomTag
    fields = ['tag']


class RoomAdmin(admin.ModelAdmin):
    inlines = [TagInline]

admin.site.register(Room, RoomAdmin)
admin.site.register(College)