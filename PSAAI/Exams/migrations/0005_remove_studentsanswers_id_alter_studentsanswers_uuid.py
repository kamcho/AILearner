# Generated by Django 4.0.2 on 2023-06-16 00:56

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('Exams', '0004_remove_studenttest_quiz'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentsanswers',
            name='id',
        ),
        migrations.AlterField(
            model_name='studentsanswers',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False),
        ),
    ]