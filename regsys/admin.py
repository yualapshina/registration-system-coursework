from django.contrib import admin
from .models import Event, Timetable, Guest, Registration

admin.site.register(Event)
admin.site.register(Timetable)
admin.site.register(Guest)
admin.site.register(Registration)