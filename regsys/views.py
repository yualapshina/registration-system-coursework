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
    categories = Timetable.objects.order_by("category").values_list("category", flat=True).distinct()
    timetable = {}
    all_tts = Timetable.objects.filter(event=request.POST["event_key"])
    for cat in categories:
        timetable.update({cat: all_tts.filter(category=cat)})
    context = {
        'timetable' : timetable,
        'guest_id' : guest.id,
    }
    return render(request, 'regsys/timetable.html', context)
    
def completed(request):
    guest_id = request.POST["guest_id"]
    guest = Guest.objects.get(id=guest_id)
    for key, value in request.POST.dict().items():
        if "category_" in key:
            t = Timetable.objects.get(id=value)
            reg = Registration(timetable=t, guest=guest)
            reg.save()
            if t.seats > 0:
                t.seats -= 1
                t.save()
    reglist = Timetable.objects.filter(registration__guest=guest_id)
    
    context = {
        'reglist' : reglist,
        'guest' : guest,
    }
    return render(request, 'regsys/completed.html', context)