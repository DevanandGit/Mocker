# Generated by Django 4.1.7 on 2023-10-29 09:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0003_merge_20231029_1524'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questions',
            name='passage',
        ),
    ]
