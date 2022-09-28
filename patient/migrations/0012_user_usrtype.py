# Generated by Django 3.2 on 2022-09-27 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0011_alter_patient_csv_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='usrtype',
            field=models.IntegerField(choices=[(1, '评分者'), (0, '管理员')], default=1, verbose_name='用户类型'),
        ),
    ]
