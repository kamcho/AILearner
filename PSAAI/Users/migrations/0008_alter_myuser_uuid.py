# Generated by Django 4.0.2 on 2023-06-22 19:14

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0007_alter_myuser_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='uuid',
            field=models.CharField(default=uuid.uuid4, max_length=100),
        ),
    ]