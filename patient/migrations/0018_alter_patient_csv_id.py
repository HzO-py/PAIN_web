# Generated by Django 3.2 on 2023-05-07 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0017_usertoken_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='csv_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='csv编号'),
        ),
    ]