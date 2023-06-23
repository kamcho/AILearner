# Generated by Django 4.0.2 on 2023-06-21 22:52

from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0003_academicprofile_grade'),
    ]

    operations = [
        migrations.CreateModel(
            name='Guardian',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('Users.myuser',),
            managers=[
                ('guardian', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Supervisor',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('Users.myuser',),
            managers=[
                ('student', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterField(
            model_name='myuser',
            name='role',
            field=models.CharField(choices=[('Student', 'Student'), ('Teacher', 'Teacher'), ('ADMINISTRATOR', 'Admin'), ('Guardian', 'Guardian'), ('Supervisor', 'Supervisor')], default='Student', max_length=15),
        ),
    ]