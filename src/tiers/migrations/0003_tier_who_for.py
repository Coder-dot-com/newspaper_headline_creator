# Generated by Django 5.0.3 on 2024-03-28 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tiers', '0002_tier_monthly_ai_credits_last_set'),
    ]

    operations = [
        migrations.AddField(
            model_name='tier',
            name='who_for',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
    ]