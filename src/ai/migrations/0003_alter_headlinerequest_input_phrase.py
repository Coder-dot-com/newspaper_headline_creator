# Generated by Django 5.0.3 on 2024-03-31 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai', '0002_headlinerequest_tone_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='headlinerequest',
            name='input_phrase',
            field=models.TextField(max_length=10000),
        ),
    ]