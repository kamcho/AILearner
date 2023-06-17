# Generated by Django 4.0.2 on 2023-06-17 02:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('SubjectList', '0022_remove_progress_topic_progress_topic'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='progress',
            name='subject',
        ),
        migrations.AddField(
            model_name='progress',
            name='subject',
            field=models.OneToOneField(default='1', on_delete=django.db.models.deletion.CASCADE, to='SubjectList.subject'),
        ),
        migrations.AlterField(
            model_name='progress',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]