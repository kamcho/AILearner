# Generated by Django 4.2.3 on 2023-08-11 03:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Teacher', '0013_alter_classtestnotifications_date'),
    ]

    operations = [
        migrations.DeleteModel(
            name='classTestStudentAnswers',
        ),
    ]