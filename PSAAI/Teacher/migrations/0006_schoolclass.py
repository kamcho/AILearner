# Generated by Django 4.2.3 on 2023-07-18 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Teacher', '0005_alter_classtest_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.PositiveIntegerField()),
                ('class_name', models.CharField(max_length=100)),
            ],
        ),
    ]