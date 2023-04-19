from django.db import models

class Event(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    date = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class Timetable(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    time = models.DateTimeField()
    place = models.CharField(max_length=100)
    host = models.CharField(max_length=100)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    seats = models.IntegerField(default=-1)
    
    def __str__(self):
        return self.name
    
class Guest(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    school = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class Registration(models.Model):
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE)
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.timetable) + " / " + str(self.guest)