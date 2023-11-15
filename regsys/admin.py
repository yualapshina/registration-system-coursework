from urllib.parse import urlencode
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Event, Timetable, Guest, Registration, Label, Labelmap

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
    list_display = ("user", "phone", "surname", "firstname", "patronymic", "school", "telegram", "photo", "registrations_link")
    
    def registrations_link(self, obj):
        count = obj.registration_set.count()
        url = (
            reverse("admin:regsys_registration_changelist")
            + "?"
            + urlencode({"guest__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">Записей: {}</a>', url, count)

    registrations_link.short_description = "Записи"

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("key", "status_verbose")
    
    def key(self, obj):
        return str(obj)
    
    def status_verbose(self, obj):
        return Registration.Status[obj.status].label
    
    key.short_description = "Ключ"
    status_verbose.short_description = "Статус"
    
@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ("label_name", "type_verbose", "events_link")
    
    def type_verbose(self, obj):
        return Label.Type[obj.type].label
    
    def events_link(self, obj):
        count = obj.labelmap_set.count()
        url = (
            reverse("admin:regsys_labelmap_changelist")
            + "?"
            + urlencode({"label__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">Событий: {}</a>', url, count)
    
    events_link.short_description = "События"
    type_verbose.short_description = "Тип"

@admin.register(Labelmap)
class LabelmapAdmin(admin.ModelAdmin):
    list_display = ("key",)
    
    def key(self, obj):
        return str(obj)
    
    key.short_description = "Ключ"