from django.db import models
from django.db.models import F, Q
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User

class Event(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    event_name = models.CharField(max_length=200, verbose_name="Название")
    start_date = models.DateField(verbose_name="Первый день")
    end_date = models.DateField(verbose_name="Последний день")
    place = models.CharField(max_length=100, verbose_name="Место")
    annotation = models.CharField(max_length=1000, verbose_name="Аннотация")
    
    def __str__(self):
        return self.event_name
        
    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError("Последний день мероприятия не может идти раньше первого")
    
    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"


class Timetable(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    timetable_name = models.CharField(max_length=200, verbose_name="Название")
    category = models.CharField(max_length=100, verbose_name="Категория")
    date = models.DateField(verbose_name="Дата")
    place = models.CharField(max_length=100, verbose_name="Место")
    host = models.CharField(max_length=100, verbose_name="Ведущий")
    annotation = models.CharField(max_length=1000, verbose_name="Аннотация")
    repeating = models.BooleanField(verbose_name="Повтор?")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name="Событие")
    seats = models.IntegerField(default=-1, verbose_name="Свободных мест")
    
    def __str__(self):
        return self.timetable_name
        
    def clean(self):
        if self.date < self.event.start_date or self.date > self.event.end_date:
            raise ValidationError("Дата не должна выходить за рамки события")
    
    class Meta:
        verbose_name = "Расписание"
        verbose_name_plural = "Расписание"
        
        
class Guest(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    surname = models.CharField(max_length=100, verbose_name="Фамилия")
    firstname = models.CharField(max_length=100, verbose_name="Имя")
    patronymic = models.CharField(max_length=100, verbose_name="Отчество")
    birthday = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    school = models.CharField(max_length=100, verbose_name="Место обучения")
    phone = models.CharField(max_length=100, verbose_name="Номер телефона")
    
    def __str__(self):
        return self.surname + " " + self.firstname
            
    class Meta:
        verbose_name = "Участник"
        verbose_name_plural = "Участники"
        
        
class Registration(models.Model):
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, verbose_name="Событие")
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, verbose_name="Участник")
    
    def __str__(self):
        return str(self.timetable) + " / " + str(self.guest)
    
    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        

@receiver(post_save, sender=Registration)
def minus_seat(sender, instance, created, **kwargs):
    if created:
        t = instance.timetable
        if t.seats > 0:
            t.seats -= 1
            t.save()
  
@receiver(pre_delete, sender=Registration)
def plus_seat(sender, instance, **kwargs):
    t = instance.timetable
    if t.seats > -1:
        t.seats += 1
        t.save()
        