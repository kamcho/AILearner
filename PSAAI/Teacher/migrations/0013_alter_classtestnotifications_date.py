# Generated by Django 4.2.3 on 2023-08-10 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Teacher', '0012_classtestnotifications_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classtestnotifications',
            name='date',
            field=models.DateTimeField(auto_created=True),
        ),
    ]