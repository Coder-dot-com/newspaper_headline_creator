# Generated by Django 5.0.3 on 2024-03-31 19:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai', '0003_alter_headlinerequest_input_phrase'),
        ('emails', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='headlinerequest',
            name='email',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='emails.useremail'),
        ),
    ]