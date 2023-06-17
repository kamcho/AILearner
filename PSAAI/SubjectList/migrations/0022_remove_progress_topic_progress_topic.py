# Generated by Django 4.0.2 on 2023-06-17 01:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SubjectList', '0021_remove_progress_subject_progress_subject'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='progress',
            name='topic',
        ),
        migrations.AddField(
            model_name='progress',
            name='topic',
            field=models.ManyToManyField(related_name='progress', to='SubjectList.Topic'),
        ),
    ]