# Generated by Django 4.0.2 on 2023-06-19 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SubjectList', '0024_alter_progress_subject_alter_topic_subject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notifications',
            name='uuid',
            field=models.CharField(default='<function uuid4 at 0x000001968C25EE50>', max_length=100, unique=True),
        ),
    ]