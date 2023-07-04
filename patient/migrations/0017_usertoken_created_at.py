# Generated by Django 3.2 on 2023-05-07 18:04

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0016_remove_patient_sample_num'),
    ]

    operations = [
        migrations.AddField(
            model_name='usertoken',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='创建时间'),
            preserve_default=False,
        ),
    ]
