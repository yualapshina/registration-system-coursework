from django.db import models
from django.db.models import F, Q
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, pre_save, pre_delete
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
        constraints = [
            models.UniqueConstraint(fields=['event_name'], name='unique name')
        ]


class Timetable(models.Model):
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    timetable_name = models.CharField(max_length=200, verbose_name="Название")
    category = models.CharField(max_length=100, verbose_name="Категория", help_text="* в категорию входит время проведения мероприятия (11.00-12.00) или его время и тип (14.00-15.00, обед); для корректности отображения расписания важно вводить время в одном формате")
    date = models.DateField(verbose_name="Дата")
    place = models.CharField(max_length=100, verbose_name="Место")
    host = models.CharField(max_length=100, verbose_name="Ведущий")
    annotation = models.CharField(max_length=1000, verbose_name="Аннотация")
    repeating = models.BooleanField(default=False, editable=False, verbose_name="Повтор?")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name="Событие")
    seats_all = models.IntegerField(default=-1, verbose_name="Всего мест")
    seats_taken = models.IntegerField(default=0, editable=False, verbose_name="Занято мест")
    
    def __str__(self):
        return self.timetable_name
        
    def clean(self):
        if self.date < self.event.start_date or self.date > self.event.end_date:
            raise ValidationError("Дата не должна выходить за рамки события")
    
    class Meta:
        verbose_name = "Элемент расписания"
        verbose_name_plural = "Элементы расписания"
        
        
class Guest(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    surname = models.CharField(max_length=100, verbose_name="Фамилия")
    firstname = models.CharField(max_length=100, verbose_name="Имя")
    patronymic = models.CharField(max_length=100, verbose_name="Отчество")
    school = models.CharField(max_length=100, verbose_name="Место обучения")
    phone = models.CharField(max_length=100, verbose_name="Номер телефона")
    telegram = models.CharField(max_length=100, verbose_name="Телеграм")
    
    def __str__(self):
        return self.user.username
            
    class Meta:
        verbose_name = "Участник"
        verbose_name_plural = "Участники"
        
        
class Registration(models.Model):
    class Status(models.TextChoices):
        AFF = "AFF", "Еще не посещено"
        INT = "INT", "Пересекается"
        WAI = "WAI", "Очередь"
        VIS = "VIS", "Посещено"
        MIS = "MIS", "Пропущено"
        
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, verbose_name="Событие")
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, verbose_name="Участник")
    status = models.CharField(choices=Status.choices, default=Status.AFF, verbose_name="Статус")
    
    def __str__(self):
        return str(self.timetable) + " / " + str(self.guest)
    
    def is_past(self):
        return self.status in {self.Status.VIS, self.Status.MIS}
        
    def is_seated(self):
        return self.status in {self.Status.AFF, self.Status.VIS, self.Status.MIS}
    
    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        constraints = [
            models.UniqueConstraint(fields=['timetable', 'guest'], name='unique Registration')
        ]
   
     
class Tag(models.Model):
    class Type(models.TextChoices):
        TAR = "TAR", "Аудитория"
        FIE = "FIE", "Направление"
        
    id = models.AutoField(primary_key=True, verbose_name="Номер")
    tag_name = models.CharField(max_length=50, verbose_name="Название", unique=True)
    type = models.CharField(choices=Type.choices, verbose_name="Тип")
    
    def __str__(self):
        return self.tag_name
    
    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class Tagmap(models.Model):  
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name="Событие")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name="Тег")
    
    def __str__(self):
        return str(self.event) + " / " + str(self.tag)
    
    class Meta:
        verbose_name = "Тег для события"
        verbose_name_plural = "Теги событий"
        constraints = [
            models.UniqueConstraint(fields=['event', 'tag'], name='unique Tagmap')
        ]

@receiver(post_save, sender=Timetable)
def add_repeat(sender, instance, created, **kwargs):
    similar = Timetable.objects.filter(~Q(id=instance.id), timetable_name=instance.timetable_name, event=instance.event)
    if similar:
        Timetable.objects.filter(id=instance.id).update(repeating=True)
        similar.update(repeating=True)
    else:
        Timetable.objects.filter(id=instance.id).update(repeating=False)

@receiver(pre_save, sender=Timetable)
def clean_repeat(sender, instance, **kwargs):
    if instance.id:
        previous = Timetable.objects.get(id=instance.id)
        similar = Timetable.objects.filter(~Q(id=instance.id), timetable_name=previous.timetable_name, event=previous.event)
        if len(similar) == 1:
            similar.update(repeating=False)
            
@receiver(pre_delete, sender=Timetable)
def clean_repeat(sender, instance, **kwargs):
    similar = Timetable.objects.filter(~Q(id=instance.id), timetable_name=instance.timetable_name, event=instance.event)
    if len(similar) == 1:
        similar.update(repeating=False)

@receiver(pre_save, sender=Registration)
def alloc_seat(sender, instance, **kwargs):
    if instance.id is None:
        if instance.is_seated:
            t = instance.timetable
            t.seats_taken += 1
            t.save()
    else:
        previous = Registration.objects.get(id=instance.id)
        t = instance.timetable
        if not previous.is_seated and instance.is_seated:
            t.seats_taken += 1
            t.save()
        if previous.is_seated and not instance.is_seated:
            t.seats_taken -= 1
            t.save()
                
@receiver(pre_delete, sender=Registration)
def free_seat(sender, instance, **kwargs):
    if instance.is_seated:
        t = instance.timetable
        t.seats_taken -= 1
        t.save()
        