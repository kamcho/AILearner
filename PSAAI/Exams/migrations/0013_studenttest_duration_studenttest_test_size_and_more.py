# Generated by Django 4.2.3 on 2023-08-04 13:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SubjectList', '0063_alter_topicalexamresults_topic'),
        ('Exams', '0012_alter_topicalquizes_subject_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='studenttest',
            name='duration',
            field=models.PositiveIntegerField(default=15),
        ),
        migrations.AddField(
            model_name='studenttest',
            name='test_size',
            field=models.PositiveIntegerField(default=15),
        ),
        migrations.AlterField(
            model_name='studenttest',
            name='topic',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='SubjectList.topic'),
        ),
    ]