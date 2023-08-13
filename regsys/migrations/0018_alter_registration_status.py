# Generated by Django 4.2 on 2023-08-12 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('regsys', '0017_event_unique_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='status',
            field=models.CharField(choices=[('AFF', 'Подтверждено'), ('INT', 'Пересекается'), ('WAI', 'Очередь'), ('VIS', 'Посещено'), ('MIS', 'Пропущено')], default='AFF', verbose_name='Статус'),
        ),
    ]