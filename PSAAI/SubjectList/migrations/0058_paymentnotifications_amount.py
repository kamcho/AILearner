# Generated by Django 4.2.3 on 2023-07-07 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SubjectList', '0057_onlineclass_link_topicexamnotifications_is_read_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentnotifications',
            name='amount',
            field=models.PositiveIntegerField(default='1'),
        ),
    ]
