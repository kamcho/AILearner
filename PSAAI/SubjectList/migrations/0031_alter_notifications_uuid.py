# Generated by Django 4.0.2 on 2023-06-22 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SubjectList', '0030_alter_notifications_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notifications',
            name='uuid',
            field=models.CharField(default='<function uuid4 at 0x000002539373EE50>', max_length=100, unique=True),
        ),
    ]
