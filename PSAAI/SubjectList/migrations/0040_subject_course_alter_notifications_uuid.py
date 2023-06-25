# Generated by Django 4.0.2 on 2023-06-23 23:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SubjectList', '0039_alter_notifications_uuid_alter_progress_subject'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='course',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='SubjectList.course'),
        ),
        migrations.AlterField(
            model_name='notifications',
            name='uuid',
            field=models.CharField(default='<function uuid4 at 0x0000024385C7EE50>', max_length=100, unique=True),
        ),
    ]
