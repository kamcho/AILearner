# Generated by Django 4.0.2 on 2023-06-17 00:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('SubjectList', '0019_alter_mysubjects_name_delete_progress'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='SubjectList.subject'),
        ),
        migrations.CreateModel(
            name='Progress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='SubjectList.subject')),
                ('subtopic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='SubjectList.subtopic')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress', to='SubjectList.topic')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
