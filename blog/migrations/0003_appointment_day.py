# Generated by Django 3.2.18 on 2023-06-28 08:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_appointment'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='day',
            field=models.DateField(default=datetime.datetime.now),
        ),
    ]
