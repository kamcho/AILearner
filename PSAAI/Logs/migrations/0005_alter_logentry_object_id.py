# Generated by Django 4.2.3 on 2023-09-09 00:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Logs', '0004_logentry_object_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logentry',
            name='object_id',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
