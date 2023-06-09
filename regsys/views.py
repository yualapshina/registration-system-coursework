import datetime
import csv
from functools import cmp_to_key
from django.http import HttpResponse
from django.shortcuts import render
from .models import Event, Timetable, Guest, Registration

@cmp_to_key
def letter_first_cmp(a, b):
    print("comparing " + a + " and " + b)
    if a[0].isdigit() and not b[0].isdigit():
        return 1
    elif not a[0].isdigit() and b[0].isdigit():
        return -1
    else:
        return (a > b) - (a < b)

def register(request):
    events = Event.objects.order_by("start_date")
    dates = []
    for event in events:
        d = []
        i = 0
        while True:
            cur_date = event.start_date + datetime.timedelta(days=i)
            d.append(cur_date)
            i += 1
            if cur_date == event.end_date:
                break
        dates.append(d)
    context = {
        'events': events,
        'dates': dates,
    }
    return render(request, 'regsys/register.html', context)

def timetable(request):
    guest = Guest(
        guest_name=request.POST["guest_name"],
        school=request.POST["school"],
        phone=request.POST["phone"],
        email=request.POST["email"],
    )
    guest.save()
    event_id = request.POST["event_key"]
    dates = []
    for key, value in request.POST.dict().items():
        if "date_" + str(event_id) in key:
            dates.append(Event.objects.get(id=event_id).start_date + datetime.timedelta(days=int(value)))
    timetable = {}
    all_tts = Timetable.objects.filter(event=event_id).order_by("date", "category", "timetable_name")
    for date in dates:
        d = {}
        dated_tts = all_tts.filter(date=date)
        cats = list(dated_tts.order_by("category").values_list("category", flat=True).distinct())
        cats.sort(key=letter_first_cmp)
        for cat in cats:
            d.update({cat: dated_tts.filter(category=cat)})
        timetable.update({date: d})
    context = {
        'timetable' : timetable,
        'guest_id' : guest.id,
        'event_id' : event_id,
    }
    return render(request, 'regsys/timetable.html', context)
    
def completed(request):
    event_id = request.POST["event_id"]
    guest_id = request.POST["guest_id"]
    guest = Guest.objects.get(id=guest_id)
    for key, value in request.POST.dict().items():
        if "category_" in key:
            t = Timetable.objects.get(id=value)
            
            unique_check = Registration.objects.filter(timetable=value).filter(guest=guest_id)
            if not unique_check:
                reg = Registration(timetable=t, guest=guest)
                reg.save()
    regs = {}
    all_regs = Timetable.objects.filter(registration__guest=guest_id).order_by("date", "category")
    dates = all_regs.order_by("date").values_list("date", flat=True).distinct()
    for date in dates:
        regs.update({date: all_regs.order_by("category").filter(date=date)})
    context = {
        'regs' : regs,
        'guest' : guest,
        'event' : Event.objects.get(id=event_id)
    }
    return render(request, 'regsys/completed.html', context)
    
def download(request):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="registration-list.csv"'},
    )
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response, delimiter =';')
    
    guest_id = request.GET["guest_id"]
    event_id = request.GET["event_id"]
    event = Event.objects.get(id=event_id)
    regs = Timetable.objects.filter(registration__guest=guest_id).order_by("date", "category")
    for reg in regs:
        writer.writerow([event.event_name + ": " + str(reg.date), reg.category, reg.timetable_name, event.place + " - " + reg.place, reg.host])

    return response