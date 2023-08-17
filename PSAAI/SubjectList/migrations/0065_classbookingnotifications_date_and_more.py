# Generated by Django 4.2.3 on 2023-08-10 12:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SubjectList', '0064_alter_topicexamnotifications_topic'),
    ]

    operations = [
        migrations.AddField(
            model_name='classbookingnotifications',
            name='date',
            field=models.DateTimeField(auto_created=True, default=datetime.datetime(2023, 8, 10, 15, 56, 59, 202124)),
        ),
        migrations.AddField(
            model_name='paymentnotifications',
            name='date',
            field=models.DateTimeField(auto_created=True, default=datetime.datetime(2023, 8, 10, 15, 56, 59, 202124)),
        ),
        migrations.AddField(
            model_name='subscriptionnotifications',
            name='date',
            field=models.DateTimeField(auto_created=True, default=datetime.datetime(2023, 8, 10, 15, 56, 59, 202124)),
        ),
        migrations.AddField(
            model_name='topicalexamresults',
            name='date',
            field=models.DateTimeField(auto_created=True, default=datetime.datetime(2023, 8, 10, 15, 56, 59, 202124)),
        ),
        migrations.AddField(
            model_name='topicexamnotifications',
            name='date',
            field=models.DateTimeField(auto_created=True, default=datetime.datetime(2023, 8, 10, 15, 56, 59, 202124)),
        ),
    ]
