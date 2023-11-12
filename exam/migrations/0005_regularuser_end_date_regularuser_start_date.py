# Generated by Django 4.1.7 on 2023-11-12 14:26

from django.db import migrations, models
import django.utils.timezone
import exam.models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0004_feedback_userresponse_exam_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='regularuser',
            name='end_date',
            field=models.DateField(blank=True, default=exam.models.calculate_end_date, null=True),
        ),
        migrations.AddField(
            model_name='regularuser',
            name='start_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
