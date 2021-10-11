# Generated by Django 3.2.7 on 2021-10-06 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0002_auto_20211005_2343'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_agent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='is_organizer',
            field=models.BooleanField(default=True),
        ),
    ]
