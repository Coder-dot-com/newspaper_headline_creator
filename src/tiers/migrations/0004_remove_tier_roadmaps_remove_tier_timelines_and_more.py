# Generated by Django 5.0.3 on 2024-03-30 23:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tiers', '0003_tier_who_for'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tier',
            name='roadmaps',
        ),
        migrations.RemoveField(
            model_name='tier',
            name='timelines',
        ),
        migrations.RemoveField(
            model_name='tier',
            name='workspaces',
        ),
    ]