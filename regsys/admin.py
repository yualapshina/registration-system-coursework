from urllib.parse import urlencode
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from .models import Event, Timetable, Guest, Registration, Label, Labelmap
    
@admin.action(description="Пометить выбранные записи как Посещённые")
def mark_visited(modeladmin, request, queryset):
    queryset.update(status=Registration.Status.VIS)
    modeladmin.message_user(
        request, 
        "Записи успешно помечены как Посещённые",
        messages.SUCCESS,
        )

@admin.action(description="Рассылка выбранным Участникам")
def mass_mail(modeladmin, request, queryset):
    selected = []
    emails = []
    if isinstance(queryset[0], Guest):
        for guest in queryset:
            selected.append(str(guest))
            emails.append(guest.user.username)
    if isinstance(queryset[0], Event):
        for event in queryset:
            selected.append(str(event))
            tts = Timetable.objects.filter(event=event)
            for tt in tts:
                regs = Registration.objects.filter(timetable=tt)
                for reg in regs:
                    emails.append(reg.guest.user.username)
    if isinstance(queryset[0], Timetable):
        for tt in queryset:
            elected.append(str(tt))
            regs = Registration.objects.filter(timetable=tt)
            for reg in regs:
                mails.append(reg.guest.user.username)
    if isinstance(queryset[0], Registration):
        for reg in queryset:
            selected.append(str(reg))
            emails.append(reg.guest.user.username)
    emails = list(set(emails))
    
    if 'apply' in request.POST:
        attachment = request.FILES.get('attachment', None)
        email = EmailMessage(
            subject=request.POST["subject"],
            body=request.POST["message"],
            from_email=settings.EMAIL_HOST_USER,
            to=[settings.EMAIL_RECEIVER],
            bcc=emails)
        if attachment:
            email.attach(attachment.name, attachment.read(), attachment.content_type)
        try:
            email.send()
        except:
            modeladmin.message_user(
                request, 
                "При отправке произошла ошибка",
                messages.ERROR,
            ) 
            return redirect(request.get_full_path())
        modeladmin.message_user(
            request, 
            "Рассылка успешно отправлена",
            messages.SUCCESS,
        ) 
        return redirect(request.get_full_path())
    
    context = modeladmin.admin_site.each_context(request) 
    context.update({
        "queryset": queryset,
        "selected": selected,
        })
    return render(request,'admin/mass_mail.html',context=context)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("event_name", "start_date", "end_date", "place", "timetables_link")
    list_filter = ["start_date", "end_date", "place"]
    search_fields = ["event_name", "start_date", "end_date", "place"]
    actions = [mass_mail]
    
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
    list_filter = ["event", "category", "date", "repeating"]
    search_fields = ["timetable_name", "event__event_name", "category", "date", "place", "host", "seats"]
    actions = [mass_mail]
    
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
    list_display = ("user", "phone", "surname", "firstname", "patronymic", "school", "telegram", "registrations_link")
    list_filter = []
    search_fields = ["user__username", "phone", "surname", "firstname", "patronymic", "school", "telegram"]
    actions = [mass_mail]
    
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
    list_filter = ["timetable__event", "status"]
    search_fields = ["timetable__timetable_name", "guest__surname", "guest__firstname", "timetable__event__event_name"]
    actions = [mass_mail, mark_visited]
    
    def key(self, obj):
        return str(obj)
    
    def status_verbose(self, obj):
        return Registration.Status[obj.status].label
    
    key.short_description = "Ключ"
    status_verbose.short_description = "Статус"
    
@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ("label_name", "type_verbose", "events_link")
    list_filter = ["type"]
    search_fields = ["label_name"]
    
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
    list_filter = ["event", "label__type"]
    search_fields = ["event__event_name", "label__label_name"]
    
    def key(self, obj):
        return str(obj)
    
    key.short_description = "Ключ"