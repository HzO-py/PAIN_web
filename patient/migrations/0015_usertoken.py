# Generated by Django 3.2 on 2023-05-04 17:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0014_delete_usertoken'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserToken',
            fields=[
                ('key', models.CharField(max_length=40, primary_key=True, serialize=False, verbose_name='用户token')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='UserToken_User', to='patient.user', verbose_name='用户')),
            ],
        ),
    ]
