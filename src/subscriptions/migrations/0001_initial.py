# Generated by Django 5.0.3 on 2024-03-28 12:37

import django.db.models.deletion
import subscriptions.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tiers', '0002_tier_monthly_ai_credits_last_set'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionChoices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('renewal_frequency', models.CharField(choices=[('monthly', 'monthly'), ('annually', 'annually')], max_length=300)),
                ('stripe_renewal_frequency', models.CharField(choices=[('month', 'month'), ('year', 'year')], max_length=300, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=7, null=True)),
                ('price_before_sale', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ('stripe_price_id', models.CharField(blank=True, max_length=300, null=True)),
                ('subscription_name', models.CharField(max_length=300, null=True)),
                ('description', models.TextField(blank=True, max_length=1000, null=True)),
                ('tier', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='tiers.tier')),
            ],
        ),
        migrations.CreateModel(
            name='UserPaymentStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('free_trial', 'free_trial'), ('active', 'active'), ('free', 'free')], max_length=300)),
                ('subscription_expiry', models.DateTimeField(blank=True, null=True)),
                ('add_free_trial_days', models.IntegerField(default=0)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('last_synced', models.DateTimeField(default=subscriptions.models.default_date_time)),
                ('tier', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tiers.tier')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserSubscriptions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('created', 'created'), ('paid', 'paid'), ('unpaid', 'unpaid'), ('cancelled', 'cancelled'), ('downgraded', 'downgraded'), ('upgraded', 'upgraded')], max_length=300)),
                ('date_subscribed', models.DateTimeField(auto_now_add=True)),
                ('stripe_customer_id', models.CharField(max_length=300)),
                ('payment_intent_id', models.CharField(blank=True, max_length=300, null=True)),
                ('subscription_id', models.CharField(blank=True, max_length=300, null=True)),
                ('interval_start_date', models.DateTimeField(blank=True, null=True)),
                ('next_due', models.DateTimeField()),
                ('payment_method', models.CharField(max_length=300)),
                ('amount_subscribed', models.DecimalField(decimal_places=2, max_digits=7)),
                ('renewal_frequency', models.CharField(max_length=300)),
                ('currency_code', models.CharField(max_length=300)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('latest_response', models.CharField(blank=True, max_length=5000, null=True)),
                ('subscription_confirmation_email_sent', models.BooleanField(default=False)),
                ('subscription_choice', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='subscriptions.subscriptionchoices')),
                ('user_payment_status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='subscriptions.userpaymentstatus')),
            ],
        ),
    ]
