# Generated by Django 4.2.3 on 2023-10-14 08:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.PositiveIntegerField()),
                ('class_name', models.CharField(max_length=100)),
                ('class_size', models.PositiveIntegerField(default=30)),
            ],
        ),
        migrations.CreateModel(
            name='MyUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('uuid', models.CharField(default=uuid.uuid4, max_length=100, unique=True)),
                ('role', models.CharField(choices=[('Student', 'Student'), ('Teacher', 'Teacher'), ('ADMINISTRATOR', 'Admin'), ('Guardian', 'Guardian')], default='Student', max_length=15)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonalProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('f_name', models.CharField(max_length=30)),
                ('ref_id', models.CharField(blank=True, max_length=100)),
                ('l_name', models.CharField(max_length=30)),
                ('surname', models.CharField(blank=True, max_length=30)),
                ('gender', models.CharField(blank=True, max_length=10)),
                ('phone', models.CharField(max_length=15, null=True, unique=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AcademicProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_class', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Users.schoolclass')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
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
            name='Student',
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
        migrations.CreateModel(
            name='Teacher',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('Users.myuser',),
            managers=[
                ('teacher', django.db.models.manager.Manager()),
            ],
        ),
    ]