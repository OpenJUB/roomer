from django.contrib import admin
from django.db.models import Q

from roomer.models import UserProfile, RoommateRequest, Room, RoomTag, College, \
    UserPreference


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


def enable_room(modeladmin, request, queryset):
    for room in queryset:
        room.remove_tag(Room.DISABLED_ROOM_TAG)
        room.save()


enable_room.short_description = "Enable all selected rooms"


def make_room_quiet(modeladmin, request, queryset):
    for room in queryset:
        room.add_tag(Room.QUIET_ROOM_TAG)
        room.save()


make_room_quiet.short_description = "Mark all selected rooms as quiet rooms"


class PreferenceInline(admin.TabularInline):
    model = UserProfile.allocation_preferences.through


class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['username', 'first_name', 'last_name', 'status']
    readonly_fields = ('points', 'year', 'major', 'country', 'old_college',
                       'housing_type', 'status')
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


class TakenFilter(admin.SimpleListFilter):
    title = 'Allocation Status'
    parameter_name = 'allocated'

    def lookups(self, request, model_admin):
        return [
            ('taken', 'Taken'),
            ('disabled', 'Free & Disabled'),
            ('free', 'Free & Allocatable'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'taken':
            return queryset.filter(~Q(assigned_user=None))
        elif self.value() == 'disabled':
            return queryset.filter(assigned_user=None).filter(tags__tag = "disabled")
        elif self.value() == 'free':
            return queryset.filter(assigned_user=None).exclude(tags__tag="disabled")
        else:
            return queryset


class RoomAdmin(admin.ModelAdmin):
    search_fields = ['code']

    list_filter = (
        'tags__tag',
        TakenFilter,
        'college',
        'block',
        'floor',
    )
    list_display = ('code', 'assigned_user')
    actions = [disable_room, enable_room, make_room_quiet]

    inlines = [TagInline]


admin.site.register(Room, RoomAdmin)
admin.site.register(College)
