from django.shortcuts import render

def register(request):
    events = {1 : "Зимняя школа", 2 : "День открытых дверей"}
    context = {
        'events': events,
    }
    return render(request, 'regsys/register.html', context)

def timetable(request):
    morning = {1: "Суперважная общая лекция"}
    afternoon = {1 : "Взламываем Пентагон на PHP", 2 : "Приходите в Сбер", 3 : "Чему я научился за три года на ПИ?"}
    evening = {1 : "Квест по нахождению выхода из вуза", 2 : "Пижамная вечеринка"}
    timetable = {"Утро" : morning, "День" : afternoon, "Вечер" : evening}
    context = {
        'timetable' : timetable,
    }
    return render(request, 'regsys/timetable.html', context)
    
def completed(request):
    context = {}
    return render(request, 'regsys/completed.html', context)