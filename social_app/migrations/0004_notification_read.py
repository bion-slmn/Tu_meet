# Generated by Django 4.2.10 on 2024-07-12 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_app', '0003_user_channel_name_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='read',
            field=models.BooleanField(default=False),
        ),
    ]
