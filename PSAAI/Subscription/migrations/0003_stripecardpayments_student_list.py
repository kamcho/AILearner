# Generated by Django 4.0.2 on 2023-06-23 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Subscription', '0002_stripecardpayments'),
    ]

    operations = [
        migrations.AddField(
            model_name='stripecardpayments',
            name='student_list',
            field=models.CharField(default='Null', max_length=100),
        ),
    ]