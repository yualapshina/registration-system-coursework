import datetime
import csv
import io
import qrcode
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from functools import cmp_to_key
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage, send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.utils import IntegrityError
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path, reverse_lazy
from django.views.generic.base import RedirectView
from .models import Event, Timetable, Guest, Registration, Label, Labelmap

navbar_sign = {
    "left": {
        "Войти": "signin",
        "Зарегистрироваться": "signup",
    },
    "right": {
        "Обратная связь": "feedback_anon",
        "Справка": "help_anon",
    }
}
navbar_profile = {
    "left": {
        "Профиль": "profile",
        "Моё расписание": "mylist",
        "Регистрация": "register",
    },
    "right": {
        "Обратная связь": "feedback",
        "Справка": "help",
        "Выйти": "signout",
    }
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
        event = Event.objects.get(id=request.POST.get("event_key", None))
        Registration.objects.filter(timetable__event=event, guest=request.user.guest).delete()
        messages.warning(request, "Регистрации на событие \"" + event.event_name + "\" удалены")
    
    if sender == "edit_info":
        guest = request.user.guest
        if request.POST.get("surname", ""):
            guest.surname = request.POST.get("surname", "")
        if request.POST.get("firstname", ""):
            guest.firstname = request.POST.get("firstname", "")
        if request.POST.get("patronymic", ""):
            guest.patronymic = request.POST.get("patronymic", "")
        if request.POST.get("school", ""):
            guest.school = request.POST.get("school", "")
        if request.POST.get("phone", ""):
            guest.phone = request.POST.get("phone", "")
        if request.POST.get("telegram", ""):
            guest.telegram = request.POST.get("telegram", "")
        guest.save()
        messages.success(request, "Изменения успешно сохранены")
        return redirect(profile)
    
    if sender == "edit_creds":
        user = authenticate(request, username=request.user.username, password=request.POST["old"])
        if user is not None:
            try:
                validate_password(request.POST["new"])
            except ValidationError:
                messages.error(request, "Пароль слишком слабый. Обратите внимание на условия")
                return redirect(profile)
            user.set_password(request.POST["new"])
            user.save()
            messages.success(request, "Пароль успешно изменён")
            return redirect(profile)
        else:
            messages.error(request, "Неверный старый пароль")
            return redirect(profile)
    
    if sender == "signup":
        email = request.POST["email"]
        password = get_random_string(10)
        needs_validation = True
        while needs_validation:
            try:
                validate_password(password)
                needs_validation = False
            except ValidationError:
                password = get_random_string(10)
        try:
            user = User.objects.create_user(username=email, password=password)
        except IntegrityError:
            messages.error(request, "К этой почте уже привязан другой аккаунт")
            return redirect(signup)
        guest = Guest(user=user)
        guest.save()
        messages.success(request, "Ваш аккаунт успешно создан")
        
        try:
            send_mail(
                subject='Аккаунт в системе регистрации ВШЭ',
                message='Вы успешно создали аккаунт в системе регистрации на мероприятия НИУ ВШЭ - Нижний Новгород. Выбирайте интересующие вас события - и увидимся там!\n\nНе забывайте заполнить личную информацию в профиле, если хотите получать именные сертификаты.\n\nВаш текущий пароль: ' + password,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email])
        except:
            messages.error(request, "При отправке письма произошла ошибка")
            return redirect(signup)
        
        messages.success(request, "Инструкции по входу отправлены на почту")
        return redirect(signin)
    
    if sender == "signin":
        user = authenticate(request, username=request.POST["email"], password=request.POST["password"])
        if user is not None:
            login(request, user)
        else:
            messages.error(request, "Неверная почта или пароль")
            return redirect(signin)
          
    if sender == "forgot":
        filter = User.objects.filter(username=request.POST["email"])
        if filter:
            user = filter[0]
            password = get_random_string(10)
            user.set_password(password)
            user.save()
            try:
                send_mail(
                    subject="Восстановление пароля в системе регистрации ВШЭ",
                    message="Вам сгенерирован новый пароль для доступа в систему регистрации на мероприятия НИУ ВШЭ. Его можно сменить после входа в профиль или оставить.\n\nНовый пароль: " + password,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.username])
            except:
                messages.error(request, "При отправке письма произошла ошибка, попробуйте снова")
                return redirect(signin)
            messages.success(request, "Инструкции по восстановлению аккаунта отправлены на почту")
            return redirect(signin)
        else:
            messages.error(request, "Аккаунт с такой почтой не найден")
            return redirect(signup)
            
    if sender == "feedback":
        guest_id = request.POST["guest_id"]
        if guest_id == "anon":
            author = request.POST["email"]
        else:
            author = Guest.objects.get(id=guest_id).user.username
        attachment = request.FILES.get('attachment', None)
        email = EmailMessage(
            subject=request.POST["subject"],
            body=request.POST["message"],
            from_email=settings.EMAIL_HOST_USER,
            to=[settings.EMAIL_RECEIVER],
            reply_to=[author])
        if attachment:
            email.attach(attachment.name, attachment.read(), attachment.content_type)
        try:
            email.send()
        except:
            messages.error(request, "При отправке сообщения произошла ошибка, попробуйте снова")
            return redirect(feedback)
        messages.success(request, "Письмо отправлено, спасибо!")
        return redirect(feedback)
          
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

def feedback_anon(request):
    if request.user.is_authenticated:
        return redirect(feedback)
    context = {
        'navbar': navbar_sign,
    }
    return render(request, 'regsys/feedback_anon.html', context)
    
def forgot(request):
    if request.user.is_authenticated:
        return redirect(mylist)
    context = {
        'navbar': navbar_sign,
    }
    return render(request, 'regsys/forgot.html', context)

def landing(request):
    if request.user.is_authenticated:
        return redirect(mylist)
    context = {
        'navbar': navbar_sign,
    }
    return render(request, 'regsys/landing.html', context)

def help_anon(request):
    if request.user.is_authenticated:
        return redirect(help)
    context = {
        'navbar': navbar_sign,
    }
    return render(request, 'regsys/help_anon.html', context)

def errors(request):
    if request.user.is_authenticated:
        return redirect(mylist)
    context = {
        'navbar': navbar_sign,
    }
    try:
        error = request.GET["submit"]
        return render(request, 'regsys/' + error + '.html', context)
    except:
        return render(request, 'regsys/errors.html', context)

@login_required
def signout(request):
    logout(request)
    return redirect(signin)

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
                d.update({entry: Registration.Status[reg.status]})
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
    all_events = Event.objects.filter().order_by("start_date")
    
    filterbar = {}
    for type in Label.Type.choices:
        t = {}
        for label in Label.objects.filter(type=type[0]):
            is_checked = "label_" + str(label.id) in request.GET.dict().keys()
            t.update({label: is_checked})
            if is_checked:
                all_events = all_events.filter(labelmap__label=label)
        filterbar.update({type: t})
    
    events_future = {}
    all_future = all_events.filter(end_date__gte=datetime.date.today())
    for event in all_future:
        labels = Label.objects.filter(labelmap__event=event)
        events_future.update({event: labels})
    context = {
        'navbar': navbar_profile,
        'filterbar': filterbar,
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
            c = {}
            for tt in dated_tts.filter(category=cat):
                c.update({tt: True if Registration.objects.filter(timetable=tt, guest=request.user.guest) else False})
            d.update({cat: c})
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
                continue
            elif category_check:
                category_check[0].delete()
            reg = Registration(timetable=t, guest=guest, status=Registration.Status.AFF)
            reg.save()
    
    messages.success(request, "Регистрация успешно обновлена")
    return redirect(mylist)

@login_required    
def download(request):
    response = HttpResponse(
        content_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="timetable.pdf"'},
    )
    
    pdfmetrics.registerFont(TTFont('HSESans-Regular', str(settings.STATIC_ROOT) + '/regsys/fonts/HSESans-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('HSESans-SemiBold', str(settings.STATIC_ROOT) + '/regsys/fonts/HSESans-SemiBold.ttf'))
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    x, y = A4
    
    event = Event.objects.get(id=request.GET["event_key"])
    can.setFont("HSESans-SemiBold", 22)
    can.setFillColorRGB(0.22, 0.29, 0.61)
    can.drawCentredString(x/2, y-50, str(event))
    textobject = can.beginText()
    textobject.setTextOrigin(64, y-70)
    
    dates = []
    i = 0
    while True:
        cur_date = event.start_date + datetime.timedelta(days=i)
        dates.append(cur_date)
        i += 1
        if cur_date == event.end_date:
            break
            
    guest = request.user.guest
    all_tts = Timetable.objects.filter(event=event, registration__guest=guest.id, date__gte=datetime.date.today()).order_by("date", "category")
    for date in dates:
        textobject.setFont("HSESans-SemiBold", 16)
        textobject.setFillColorRGB(0.52, 0.52, 0.53)
        textobject.textLine()
        textobject.textLine(date.strftime('%d.%m.%Y'))
        
        dated_tts = all_tts.filter(date=date)
        cats = list(dated_tts.order_by("category").values_list("category", flat=True).distinct())
        cats.sort(key=letter_first_cmp)
        for cat in cats:
            tt = dated_tts.filter(category=cat)[0]
            tt_str = str(tt.category) + ':  ' + str(tt.timetable_name) + ',  ' + str(tt.place)
            textobject.setFont("HSESans-Regular", 16)
            textobject.setFillColorRGB(0.52, 0.52, 0.53)
            textobject.textLine(tt_str)
    
    can.drawText(textobject)
    can.showPage()
    can.save()
    packet.seek(0)
    new_pdf = PdfReader(packet)
    output = PdfWriter(response)
    for i in range(len(new_pdf.pages)):
        page = new_pdf.pages[i]
        output.add_page(page)
    output.write(response)
    
    return response
    
@login_required    
def feedback(request):   
    guest = request.user.guest
    context = {
        'guest' : guest,
        'navbar': navbar_profile,
    }
    return render(request, 'regsys/feedback.html', context)

@login_required   
def help(request):
    guest = request.user.guest
    context = {
        'guest' : guest,
        'navbar': navbar_profile,
    }
    return render(request, 'regsys/help.html', context)
    
@login_required    
def certificate(request):
    response = HttpResponse(
        content_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="certificate.pdf"'},
    )
    
    event = Event.objects.get(id=request.GET["event_key"])
    guest = request.user.guest
    regs = Registration.objects.filter(guest=guest, status=Registration.Status.VIS, timetable__event=event)
    
    pdfmetrics.registerFont(TTFont('HSESans-Regular', str(settings.STATIC_ROOT) + '/regsys/fonts/HSESans-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('HSESans-SemiBold', str(settings.STATIC_ROOT) + '/regsys/fonts/HSESans-SemiBold.ttf'))
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    x, y = A4
    
    #TODO line wrapping
    can.setFont("HSESans-SemiBold", 24)
    can.setFillColorRGB(0.22, 0.29, 0.61)
    can.drawCentredString(x/2, y-310, str(guest))
    can.setFillColorRGB(0.15, 0.22, 0.51)
    can.drawCentredString(x/2, y-428, str(event))
    date_str = event.start_date.strftime('%d.%m.%Y')
    if event.start_date != event.end_date:
        date_str = 'с ' + event.start_date.strftime('%d.%m.%Y') + ' по ' + event.end_date.strftime('%d.%m.%Y')
    can.setFont("HSESans-Regular", 16)
    can.setFillColorRGB(0.52, 0.52, 0.53)
    can.drawCentredString(x/2, y-468, date_str)
    can.showPage()
    
    textobject = can.beginText()
    textobject.setFont("HSESans-Regular", 16)
    textobject.setFillColorRGB(0.52, 0.52, 0.53)
    textobject.setTextOrigin(64, y-160)
    for reg in regs:
        textobject.textLine(str(reg.timetable))
    can.drawText(textobject)
    can.save()
    packet.seek(0)
    
    new_pdf = PdfReader(packet)
    template_pdf = PdfReader(open(str(settings.STATIC_ROOT) + '/regsys/template-certificate.pdf', 'rb'))
    output = PdfWriter(response)
    for i in range(len(template_pdf.pages)):
        page = template_pdf.pages[i]
        page.merge_page(new_pdf.pages[i])
        output.add_page(page)
    output.write(response)
    
    return response
    
@login_required    
def qr_generate(request):
    response = HttpResponse(
        content_type="image/png",
        headers={"Content-Disposition": 'attachment; filename="qr.png"'},
    )
    
    link = 'http://127.0.0.1:8000/qr/read/'
    link += '?timetable=' + str(request.GET["timetable"])
    link += '&guest=' + str(request.GET["guest"])
    qr = qrcode.QRCode()
    qr.add_data(link)
    qr.make()
    img = qr.make_image(back_color=(232,234,244), fill_color=(26,39,109))
    img.save(response)
    return response
    
@staff_member_required
def qr_read(request):
    timetable = Timetable.objects.get(id=request.GET["timetable"])
    guest = Guest.objects.get(id=request.GET["guest"])  
    try:
        reg = Registration.objects.get(timetable=timetable, guest=guest)
        if reg.status == Registration.Status.AFF:
            reg.status = Registration.Status.VIS
            reg.save()
        link = '../../admin/regsys/registration/'
        link += '?timetable=' + str(request.GET["timetable"])
        link += '&guest=' + str(request.GET["guest"])
        return redirect(link)
    except:
        pass
    return redirect('admin:index')
    
@staff_member_required   
def help_admin(request):
    response = HttpResponse(
        open(str(settings.STATIC_ROOT) + '/regsys/help-admin.pdf', 'rb'),
        content_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="help-admin.pdf"'},
    )
    return response