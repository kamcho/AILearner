# Generated by Django 4.0.2 on 2023-06-19 12:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Exams', '0007_studenttest_marks_alter_studentsanswers_test_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentsanswers',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Exams.studenttest'),
        ),
    ]
