from django.shortcuts import render
from .models import Event, Timetable, Guest, Registration

def register(request):
    events = Event.objects.all()
    context = {
        'events': events,
    }
    return render(request, 'regsys/register.html', context)

def timetable(request):
    guest = Guest(
        name=request.POST["name"],
        school=request.POST["school"],
        phone=request.POST["phone"],
        email=request.POST["email"],
    )
    guest.save()
    timetable = Timetable.objects.filter(event=request.POST["event_key"])
    context = {
        'timetable' : timetable,
        'guest_id' : guest.id,
    }
    return render(request, 'regsys/timetable.html', context)
    
def completed(request):
    guest_id = request.POST["guest_id"]
    for key, value in request.POST.dict().items():
        if "entry_" in key:
            reg = Registration(
                timetable=Timetable.objects.get(id=value),
                guest=Guest.objects.get(id=guest_id),
            )
            reg.save()
    reglist = Timetable.objects.filter(registration__guest=guest_id)
    quest = Guest.objects.get(id=guest_id)
    context = {
        'reglist' : reglist,
        'guest' : Guest.objects.get(id=guest_id),
    }
    return render(request, 'regsys/completed.html', context)