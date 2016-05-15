from django.contrib import admin
from roomer.models import UserProfile, RoommateRequest, Room, RoomTag, College, UserPreference


def make_tall(modeladmin, request, queryset):
    queryset.update(is_tall=True)


make_tall.short_description = "Add tall flag to selected users"


def unmake_tall(modeladmin, request, queryset):
    queryset.update(is_tall=False)


unmake_tall.short_description = "Remove tall flag from selected users"


def disable_room(modeladmin, request, queryset):
    for room in queryset:
        room.add_tag(Room.DISABLED_ROOM_TAG)
        room.save()


disable_room.short_description = "Disable all selected rooms"

class PreferenceInline(admin.TabularInline):
    model = UserProfile.allocation_preferences.through


class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['username', 'first_name', 'last_name']
    readonly_fields = ('points', 'year', 'major', 'country', 'old_college', 'seniority')
    model = UserProfile

    list_filter = ('college', 'old_college', 'major', 'year')
    actions = [make_tall, unmake_tall]

    inlines = [
        PreferenceInline
    ]


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(RoommateRequest)
admin.site.register(UserPreference)


class TagInline(admin.TabularInline):
    model = RoomTag
    fields = ['tag']


class RoomAdmin(admin.ModelAdmin):
    search_fields = ['code']

    list_filter = ('college', 'block', 'floor')
    list_display = ('code', 'assigned_user')
    actions = [disable_room]

    inlines = [TagInline]


admin.site.register(Room, RoomAdmin)
admin.site.register(College)
