# Generated by Django 4.2 on 2023-08-14 10:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('regsys', '0020_alter_registration_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='Номер')),
                ('label_name', models.CharField(max_length=50, verbose_name='Название')),
                ('type', models.CharField(choices=[('TAR', 'Аудитория'), ('FIE', 'Направление'), ('CON', 'Подтверждение')], verbose_name='Тип')),
            ],
            options={
                'verbose_name': 'Лейбл',
                'verbose_name_plural': 'Лейблы',
            },
        ),
        migrations.CreateModel(
            name='Labelmap',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='regsys.event', verbose_name='Событие')),
                ('label', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='regsys.label', verbose_name='Лейбл')),
            ],
            options={
                'verbose_name': 'Лейблмап',
            },
        ),
    ]
