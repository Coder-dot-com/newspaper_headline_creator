# Generated by Django 5.0.3 on 2024-03-28 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionchoices',
            name='monthly_price',
            field=models.DecimalField(decimal_places=2, max_digits=7, null=True),
        ),
    ]
