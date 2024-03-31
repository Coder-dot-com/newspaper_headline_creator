from django.db import models
from django.contrib.auth import get_user_model
from datetime import  datetime, timedelta
from django.utils import timezone
from django.db.models import Q

from tiers.models import Tier
import stripe
from newspaper_headline_creator.settings import STRIPE_SECRET_KEY
from tiers.models import UserTier, Tier
# from ai.models import UserAI

User = get_user_model()

stripe.api_key = STRIPE_SECRET_KEY



# Create your models here.
choices = [
    ("free_trial", "free_trial"),
    ("active", "active"),
    ("free", "free"),
]

def default_date_time():
    now = datetime.now()
    return now - timedelta(days=100)


class UserPaymentStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=300, choices=choices)
    subscription_expiry = models.DateTimeField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_synced = models.DateTimeField(default=default_date_time)
 
    def sync_subscription_expiry_model_method(self):
        if self.subscription_expiry and self.subscription_expiry <  timezone.now():
            print("SYncing subscription")

            user_subscription = UserSubscriptions.objects.filter(Q(
                    user_payment_status=self,
                    status="paid")| Q(user_payment_status=self,
                    status="cancelled")).latest('created_at')
            
            
            #set user payment and user tier and user ai according to this user subscription based on if its expired 
            #or not
            self.subscription_expiry =  user_subscription.next_due
            self.save()

            #if still expired after checking for latest subscriptions
            if self.subscription_expiry <  timezone.now():
                self.status = 'free'
                self.save()
                #set tier back to free and update user ai credits to free tier value
                user = self.user
                #update user tier
                user_tier = UserTier.objects.get(user=user)
                free_tier = Tier.objects.filter(type="free_tier").first()
                user_tier.tier = free_tier
                user_tier.save()
                #set user monthly credits only run once
                user_ai = UserAI.objects.get(user=user)
                user_ai.monthly_ai_credits_remaining = user_tier.tier.monthly_ai_credits
                user_ai.save()
                
            else:
                #set the correct plan
                self.status = 'active'
                self.save()
                #set tier back to free and update user ai credits to free tier value
                user = self.user
                #update user tier
                user_tier = UserTier.objects.get(user=user)
                #set the correct tier

                tier = user_subscription.subscription_choice.tier

                user_tier.tier = tier
                user_tier.save()
                #set user monthly credits only run once
                user_ai = UserAI.objects.get(user=user)
                user_ai.monthly_ai_credits_remaining = user_tier.tier.monthly_ai_credits
                user_ai.save()
                


subscription_choices = [
    ("monthly", "monthly"),
    ("annually", "annually"),
]

stripe_interval_choices = [
    ("month", "month"),
    ("year", "year"),
]
    
class SubscriptionChoices(models.Model):
    #IF UPDATING REMEMBER TO MODIFY MODEL METHODS ALSO 
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE, null=True)
    # currency = models.ForeignKey(Currency, null=True, on_delete=models.SET_NULL)
    # create_nonusd_subscriptions = models.BooleanField(default=False)
    renewal_frequency =  models.CharField(max_length=300, choices=subscription_choices)
    stripe_renewal_frequency =  models.CharField(max_length=300, choices=stripe_interval_choices, null=True)
    monthly_price = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    price =  models.DecimalField(max_digits=7, decimal_places=2, null=True)
    price_before_sale =  models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    stripe_price_id = models.CharField(max_length=300, null=True, blank=True)
    subscription_name = models.CharField(max_length=300, null=True)
    description = models.TextField(max_length=1000, blank=True, null=True)

    
subscription_statuses = [
    ("created", "created"),
    ("paid", "paid"),
    ("cancelled", "cancelled"),

]

class UserSubscriptions(models.Model):
    user_payment_status = models.ForeignKey(UserPaymentStatus, on_delete=models.SET_NULL, null=True)
    subscription_choice = models.ForeignKey(SubscriptionChoices, on_delete=models.SET_NULL, null=True)
    
    status = models.CharField(max_length=300, choices=subscription_statuses)

    date_subscribed = models.DateTimeField(auto_now_add=True)
    stripe_customer_id = models.CharField(max_length=300)    
    payment_intent_id = models.CharField(max_length=300, null=True,blank=True)
    subscription_id = models.CharField(max_length=300, null=True, blank=True)

    interval_start_date = models.DateTimeField(null=True, blank=True) 
    next_due = models.DateTimeField()
    payment_method = models.CharField(max_length=300)
    amount_subscribed =  models.DecimalField(max_digits=7, decimal_places=2)
    renewal_frequency =  models.CharField(max_length=300)
    currency_code = models.CharField(max_length=300) 
    created_at = models.DateTimeField(auto_now_add=True)
    latest_response = models.CharField(max_length=5000, blank=True, null=True)
    subscription_confirmation_email_sent = models.BooleanField(default=False)