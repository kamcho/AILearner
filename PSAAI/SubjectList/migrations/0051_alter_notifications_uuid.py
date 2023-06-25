# Generated by Django 4.0.2 on 2023-06-25 18:49

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('SubjectList', '0050_alter_notifications_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notifications',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
