# Generated by Django 4.2.10 on 2024-07-06 14:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social_app', '0003_alter_comment_options_alter_like_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['created_at']},
        ),
        migrations.AlterModelOptions(
            name='like',
            options={'ordering': ['created_at']},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['created_at']},
        ),
    ]
