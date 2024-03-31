from newspaper_headline_creator.celery import app
from celery.utils.log import get_task_logger

from datetime import datetime, timedelta, timezone
from .models import UserPaymentStatus, UserSubscriptions
from django.db.models import Q
from newspaper_headline_creator.settings import STRIPE_SECRET_KEY, STRIPE_PUBLIC_KEY
from tiers.models import UserTier, Tier
# from ai.models import UserAI


import stripe

stripe.api_key = STRIPE_SECRET_KEY

stripe_pub_key = STRIPE_PUBLIC_KEY
logger = get_task_logger(__name__)



@app.task
def cancel_subscription(user_payment_status_id):
        print("Canelling subscription...")
        #Call stripe api using subscription id from latest

        user_payment_status = UserPaymentStatus.objects.get(id=user_payment_status_id)
        
        # I.e,. check if current time greater than subscription_expiry
        try:
            user_subscription = UserSubscriptions.objects.filter(Q(
                user_payment_status=user_payment_status,
                status="paid")| Q(user_payment_status=user_payment_status,
                status="created")).latest('created_at')
        except UserSubscriptions.DoesNotExist:
            user_subscription = None

        print(user_subscription)
        if user_subscription:
            

                #check if tier has changed and if has re update the monthly ai credits and also the tier to the correct current tier
            #as don;t have retry setup in stripe settings it auto cancels               
            user_subscription.status = "cancelled"
            user_subscription.save()
            print("Subscription cancelled")
            user_payment_status.status = 'free'
            user_payment_status.save()
                #set tier back to free and update user ai credits to free tier value
            user = user_payment_status.user
                #update user tier
            user_tier = UserTier.objects.get(user=user)
            free_tier = Tier.objects.filter(type="free_tier").first()
            user_tier.tier = free_tier
            user_tier.save()
            #set user monthly credits only run once
            user_ai = UserAI.objects.get(user=user)
            user_ai.monthly_ai_credits_remaining = user_tier.tier.monthly_ai_credits
            user_ai.save()
             #call function in webhook

                        

