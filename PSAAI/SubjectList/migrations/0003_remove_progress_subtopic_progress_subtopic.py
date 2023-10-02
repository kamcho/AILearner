# Generated by Django 4.2.3 on 2023-09-18 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SubjectList', '0002_topic_test_size_topic_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='progress',
            name='subtopic',
        ),
        migrations.AddField(
            model_name='progress',
            name='subtopic',
            field=models.ManyToManyField(related_name='progress_subtopic', to='SubjectList.subtopic'),
        ),
    ]
