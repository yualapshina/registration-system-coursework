from urllib.parse import urlencode
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Event, Timetable, Guest, Registration

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("event_name", "start_date", "end_date", "place", "timetables_link")
    
    def timetables_link(self, obj):
        count = obj.timetable_set.count()
        url = (
            reverse("admin:regsys_timetable_changelist")
            + "?"
            + urlencode({"event__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">Мероприятий: {}</a>', url, count)

    timetables_link.short_description = "Расписание"

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ("timetable_name", "event", "category", "date", "place", "host", "repeating", "seats", "registrations_link")
    
    def registrations_link(self, obj):
        count = obj.registration_set.count()
        url = (
            reverse("admin:regsys_registration_changelist")
            + "?"
            + urlencode({"timetable__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">Записей: {}</a>', url, count)

    registrations_link.short_description = "Записи"

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ("guest_name", "school", "registrations_link")
    
    def registrations_link(self, obj):
        count = obj.registration_set.count()
        url = (
            reverse("admin:regsys_registration_changelist")
            + "?"
            + urlencode({"guest__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">Записей: {}</a>', url, count)

    registrations_link.short_description = "Записи"

admin.site.register(Registration)