# Generated by Django 4.2.3 on 2023-08-12 21:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Exams', '0020_studentsanswers_uuid_alter_classtest_uuid_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='StudentKNECExams',
        ),
    ]
