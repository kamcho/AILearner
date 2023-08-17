# Generated by Django 4.2.3 on 2023-08-11 04:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('SubjectList', '0066_alter_classbookingnotifications_date_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Users', '0014_remove_personalprofile_pic'),
        ('Exams', '0016_studentsanswers_test_content_type_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassTest',
            fields=[
                ('uuid', models.CharField(default=uuid.uuid4, max_length=100, primary_key=True, serialize=False, unique=True)),
                ('test_size', models.PositiveIntegerField()),
                ('duration', models.PositiveIntegerField(default='15')),
                ('expiry', models.DateField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('class_id', models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, to='Users.schoolclass')),
                ('quiz', models.ManyToManyField(to='Exams.topicalquizes')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='SubjectList.subject')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='studentsanswers',
            name='test_object_id',
            field=models.UUIDField(),
        ),
        migrations.CreateModel(
            name='ClassTestStudentTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(default=uuid.uuid4, max_length=100, unique=True)),
                ('date', models.DateTimeField(auto_now=True)),
                ('marks', models.CharField(default='0', max_length=100)),
                ('finished', models.BooleanField()),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Exams.classtest')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]