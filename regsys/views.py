import datetime
import csv
from functools import cmp_to_key
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.utils import IntegrityError
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Event, Timetable, Guest, Registration

navbar_sign = {
    "Вход в профиль": "signin",
    "Создание профиля": "signup",
}
navbar_profile = {
    "Профиль": "profile",
    "Моё расписание": "mylist",
    "Зарегистрироваться": "register",
}

@cmp_to_key
def letter_first_cmp(a, b):
    if a[0].isdigit() and not b[0].isdigit():
        return 1
    elif not a[0].isdigit() and b[0].isdigit():
        return -1
    else:
        return (a > b) - (a < b)

def dispatcher(request):
    sender = request.POST.get("submit", "")
    if not sender:
        sender = request.GET.get("submit", "")
    
    if sender == "delete":
        reg = Registration.objects.get(timetable=request.GET["entry_id"], guest=request.user.guest)
        messages.warning(request, "Регистрация \"" + reg.timetable.timetable_name + "\" удалена")
        reg.delete()
        return redirect(mylist)
    
    if sender == "edit_info":
        guest = request.user.guest
        if request.POST.get("surname", ""):
            guest.surname = request.POST.get("surname", "")
        if request.POST.get("firstname", ""):
            guest.firstname = request.POST.get("firstname", "")
        if request.POST.get("patronymic", ""):
            guest.patronymic = request.POST.get("patronymic", "")
        if request.POST.get("phone", ""):
            guest.phone = request.POST.get("phone", "")
        if request.POST.get("school", ""):
            guest.school = request.POST.get("school", "")
        guest.save()
        messages.success(request, "Изменения успешно сохранены")
        return redirect(profile)
    
    if sender == "edit_creds":
        user = authenticate(request, username=request.user.username, password=request.POST["old"])
        if user is not None:
            user.set_password(request.POST["new"])
            user.save()
            messages.success(request, "Пароль успешно изменён")
            return redirect(profile)
        else:
            messages.error(request, "Неверный старый пароль")
            return redirect(profile)
    
    if sender == "signout":
        logout(request)
    
    if sender == "signup":
        guest = request.user.guest
        guest.surname = request.POST.get("surname", "")
        guest.firstname = request.POST.get("firstname", "")
        guest.patronymic = request.POST.get("patronymic", "")
        guest.school = request.POST.get("school", "")
        guest.phone = request.POST.get("phone", "")
        guest.save()
        messages.success(request, "Профиль успешно создан")
    
    if sender == "signin":
        
        user = authenticate(request, username=request.POST["email"], password=request.POST["password"])
        if user is not None:
            login(request, user)
        else:
            messages.error(request, "Неверная почта или пароль")
            return redirect(signin)
            
    return redirect(mylist)
            
def signin(request):
    if request.user.is_authenticated:
        return redirect(mylist)
    context = {
        'navbar': navbar_sign,
    }
    return render(request, 'regsys/signin.html', context)

def signup(request):
    if request.user.is_authenticated:
        return redirect(mylist)
    context = {
        'navbar': navbar_sign,
    }
    return render(request, 'regsys/signup.html', context)
    
def personal(request):
    if request.POST.get("submit", "") != "to_personal":
        return redirect(mylist)

    email = request.POST["email"]
    password = request.POST["password"]
    if request.POST["repeat"] != password:
        messages.error(request, "Пароль не совпадает")
        return redirect(signup)
    try:
        user = User.objects.create_user(username=email, password=password)
    except IntegrityError:
        messages.error(request, "Профиль с такой почтой уже существует")
        return redirect(signup)
    guest = Guest(user=user)
    guest.save()
    user = authenticate(request, username=email, password=password)
    if user is not None:
        login(request, user)
    else:
        messages.error(request, "Ошибка при создании")
        return redirect(signup)
    context = {
        'navbar': navbar_sign,
    }
    return render(request, 'regsys/personal.html', context)

@login_required
def mylist(request):
    guest = request.user.guest
            
    regs_past = {}
    regs_future = {}
    all_regs = Timetable.objects.filter(registration__guest=guest.id).order_by("event__start_date", "date", "category")
    
    events_list = all_regs.order_by("event__event_name").values_list("event__event_name", flat=True).distinct()
    events = []
    for name in events_list:
        events.append(Event.objects.filter(event_name=name)[0])
    for event in events:
        e_past = {}
        e_future = {}
        dates = all_regs.filter(event=event).order_by("date").values_list("date", flat=True).distinct()
        for date in dates:
            d = {}
            entries = all_regs.order_by("category").filter(event=event, date=date)
            for entry in entries:
                reg = Registration.objects.get(timetable=entry, guest=guest)
                if reg.status == Registration.Status.INT and not Registration.objects.filter(guest=guest, status=Registration.Status.AFF, timetable__category=entry.category):
                    reg.status = Registration.Status.AFF
                    reg.save() 
                    messages.success(request, "Пересечения в категории \"" + entry.category + "\" исправлены")
                if date < datetime.date.today() and not reg.is_past():
                    reg.status = Registration.Status.MIS
                    reg.save()
                d.update({entry: Registration.Status[reg.status].label})
            if date >= datetime.date.today():
                e_future.update({date: d})
            else:
                e_past.update({date: d})
        if e_past:
            regs_past.update({event: e_past})
        if e_future:
            regs_future.update({event: e_future})
        
    context = {
        'regs_past' : regs_past,
        'regs_future' : regs_future,
        'guest' : guest,
        'navbar': navbar_profile,
    }
    return render(request, 'regsys/mylist.html', context)

@login_required
def profile(request):
    context = {
        'guest': request.user.guest,
        'navbar': navbar_profile,
    }
    return render(request, 'regsys/profile.html', context)

@login_required
def register(request):
    events_past = Event.objects.filter(end_date__lt=datetime.date.today()).order_by("start_date")
    events_future = Event.objects.filter(end_date__gte=datetime.date.today()).order_by("start_date")
    context = {
        'navbar': navbar_profile,
        'events_past': events_past,
        'events_future': events_future,
    }
    return render(request, 'regsys/register.html', context)

@login_required
def timetable(request):
    event_id = request.POST.get("event_key", None)
    if not event_id:
        return redirect(register)
    event = Event.objects.get(id=event_id)
    
    dates = []
    i = 0
    while True:
        cur_date = event.start_date + datetime.timedelta(days=i)
        dates.append(cur_date)
        i += 1
        if cur_date == event.end_date:
            break
    
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
        'event' : event,
        'navbar': navbar_profile,
    }
    return render(request, 'regsys/timetable.html', context)

@login_required    
def completed(request):
    if request.POST.get("submit", "") != "to_completed":
        return redirect(register)
        
    event_id = request.POST["event_id"]
    guest = request.user.guest
    for key, value in request.POST.dict().items():
        if "category_" in key:
            t = Timetable.objects.get(id=value)
            
            unique_check = Registration.objects.filter(timetable=t, guest=guest)
            category_check = Registration.objects.filter(timetable__category=t.category, guest=guest, status=Registration.Status.AFF)
            if unique_check:
                messages.warning(request, t.timetable_name +" уже в расписании")
            elif category_check:
                reg = Registration(timetable=t, guest=guest, status=Registration.Status.INT)
                reg.save()
                messages.warning(request, "В категории \"" + t.category + "\" есть пересечения. Чтобы подтвердить новую запись, удалите старую")
            else: 
                reg = Registration(timetable=t, guest=guest, status=Registration.Status.AFF)
                reg.save()
    
    messages.success(request, "Регистрация успешно завершена")
    return redirect(mylist)

@login_required    
def download(request):
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="registration-list.csv"'},
    )
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response, delimiter =';')
    
    guest = request.user.guest
    regs = Timetable.objects.filter(registration__guest=guest.id).order_by("date", "category")
    for reg in regs:
        writer.writerow([reg.event.event_name + ": " + str(reg.date), reg.category, reg.timetable_name, reg.event.place + " - " + reg.place, reg.host, Registration.objects.get(timetable=reg, guest=guest).status])

    return response