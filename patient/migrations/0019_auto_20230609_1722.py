# Generated by Django 3.2 on 2023-06-09 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0018_alter_patient_csv_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='aiscore',
            name='diastolic_pressure',
            field=models.FloatField(blank=True, null=True, verbose_name='舒张压'),
        ),
        migrations.AddField(
            model_name='aiscore',
            name='heart_rate',
            field=models.FloatField(blank=True, null=True, verbose_name='心率'),
        ),
        migrations.AddField(
            model_name='aiscore',
            name='systolic_pressure',
            field=models.FloatField(blank=True, null=True, verbose_name='收缩压'),
        ),
    ]
