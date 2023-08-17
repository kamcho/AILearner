# Generated by Django 4.2.3 on 2023-08-12 19:31

import Exams.models
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('Exams', '0019_alter_generaltest_exam_type_studentknecexams_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentsanswers',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='classtest',
            name='uuid',
            field=Exams.models.UniqueUUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='generaltest',
            name='uuid',
            field=Exams.models.UniqueUUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name='knecgradeexams',
            name='uuid',
            field=Exams.models.UniqueUUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='studentknecexams',
            name='uuid',
            field=Exams.models.UniqueUUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AlterField(
            model_name='studenttest',
            name='uuid',
            field=Exams.models.UniqueUUIDField(default=uuid.uuid4, unique=True),
        ),
    ]