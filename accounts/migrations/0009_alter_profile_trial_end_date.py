# Generated by Django 5.1.1 on 2024-09-14 10:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_alter_profile_trial_end_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='trial_end_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 9, 17, 10, 40, 41, 433478, tzinfo=datetime.timezone.utc)),
        ),
    ]
