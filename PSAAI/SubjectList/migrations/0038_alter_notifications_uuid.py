# Generated by Django 4.0.2 on 2023-06-23 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SubjectList', '0037_alter_notifications_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notifications',
            name='uuid',
            field=models.CharField(default='<function uuid4 at 0x000001833B75EE50>', max_length=100, unique=True),
        ),
    ]