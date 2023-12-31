# Generated by Django 4.2.7 on 2023-11-21 16:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0005_regularuser_end_date_regularuser_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='regularuser',
            name='username',
            field=models.CharField(max_length=100, unique=True, validators=[django.core.validators.RegexValidator('^(PRP|prp)[0-9]{2}([A-Za-z]{2}|[0-9]{2})[0-9]{3}$')]),
        ),
    ]
