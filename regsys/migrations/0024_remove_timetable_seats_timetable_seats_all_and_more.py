# Generated by Django 4.2 on 2024-05-16 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regsys', '0023_remove_guest_photo_alter_guest_telegram'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timetable',
            name='seats',
        ),
        migrations.AddField(
            model_name='timetable',
            name='seats_all',
            field=models.IntegerField(default=-1, verbose_name='Всего мест'),
        ),
        migrations.AddField(
            model_name='timetable',
            name='seats_available',
            field=models.IntegerField(default=-1, editable=False, verbose_name='Свободных мест'),
        ),
        migrations.AlterField(
            model_name='label',
            name='type',
            field=models.CharField(choices=[('TAR', 'Аудитория'), ('FIE', 'Направление')], verbose_name='Тип'),
        ),
        migrations.AlterField(
            model_name='timetable',
            name='repeating',
            field=models.BooleanField(default=False, editable=False, verbose_name='Повтор?'),
        ),
    ]