from django.contrib import admin

from .models import *


# Register your models here.

class RoomPhaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'points_limit', 'start', 'end')
    date_hierarchy = 'end'

admin.site.register(RoomPhase, RoomPhaseAdmin)
