# Generated by Django 4.2 on 2023-05-08 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regsys', '0006_event_end_date_check'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='event',
            name='end_date_check',
        ),
        migrations.AddConstraint(
            model_name='event',
            constraint=models.CheckConstraint(check=models.Q(('end_date__gte', models.F('start_date'))), name='early_end_date_check', violation_error_message='Последний день мероприятия не может идти раньше первого'),
        ),
        migrations.AddConstraint(
            model_name='registration',
            constraint=models.UniqueConstraint(fields=('timetable', 'guest'), name='reg_unique', violation_error_message='Вы уже зарегистрировались на это мероприятие'),
        ),
    ]
