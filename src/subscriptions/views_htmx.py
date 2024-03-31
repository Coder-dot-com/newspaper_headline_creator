from django.shortcuts import render, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import SubscriptionChoices, UserPaymentStatus, UserSubscriptions
from datetime import datetime, timezone

from newspaper_headline_creator.settings import STRIPE_SECRET_KEY, STRIPE_PUBLIC_KEY
from django.db.models import Q

import stripe

stripe.api_key = STRIPE_SECRET_KEY

stripe_pub_key = STRIPE_PUBLIC_KEY


@login_required
def subscribe_modal_htmx(request, choice_id):
    choice = SubscriptionChoices.objects.get(id=choice_id)
    context = {
        'choice': choice,
    }
    
    user = request.user
    user_email = user.email


    #Get the user  payment status object or create
    #Then check if page status is currently active or not if active check if there is already an 
    # active subscription if active subscription then just display the current subscription
     #Then same check will also be added on subscription page load for the display part
    try:
        user_payment_status = UserPaymentStatus.objects.get(user=user)
        user_subscription = None
        if user_payment_status.status == "active":
            try:
                user_subscription = UserSubscriptions.objects.get(user_payment_status=user_payment_status, status="paid")
                if user_subscription:
                    #Here render the subscription and ability to cancel
                    return render(request, "includes/pre_existing_payment_method_modal.html") 
              
            except:
                pass


    except UserPaymentStatus.DoesNotExist:
        user_payment_status = UserPaymentStatus.objects.create(user=user,status="free")


    customer = stripe.Customer.create(
        email=user_email)
    
    customer_id = customer.id

    price = choice.price
    
    price_id = choice.stripe_price_id
    #no free trial
    trial_period_days = 0
    current_time = datetime.now(timezone.utc)


    try:


        user_subscription = UserSubscriptions.objects.filter(
            user_payment_status=user_payment_status,
            status="cancelled", 

            ).latest('created_at')
        
    except:
        pass

    
    try:
        # Check if higher tier cancelled subscription available
        user_subscription_with_greater_tier = UserSubscriptions.objects.filter(Q(
                        user_payment_status=user_payment_status,
                        status="cancelled"),
                        next_due__gt= current_time,
                        subscription_choice__tier__tier_ranking__gt=user_subscription.subscription_choice.tier.tier_ranking).order_by((
                            'subscription_choice__tier__tier_ranking')).reverse()[0]
        if user_subscription_with_greater_tier.next_due.replace(tzinfo=None)  > datetime.now().replace(tzinfo=None):
                    user_subscription = user_subscription_with_greater_tier
                    
    except:
            pass


    if user_subscription:

        start_date = user_subscription.next_due
        print(start_date)


        # Need to delay days even if user is resubscribing to ensure new susbcription only starts after
        days_left = int((start_date - current_time).days)
        print('days_left', days_left)

        # Here need to convert days to new plan only if tier gte to current 
        if choice.tier.tier_ranking >= user_subscription.subscription_choice.tier.tier_ranking:
            
            print("Subscription greater")

            if user_subscription.subscription_choice.stripe_renewal_frequency == "month":
                print("month")
                total_value_of_days_left = (user_subscription.subscription_choice.price/30) * days_left
            elif user_subscription.subscription_choice.stripe_renewal_frequency == "year":
                print("year")
                total_value_of_days_left = (user_subscription.subscription_choice.price/365) * days_left

            #to do for multicurrency use the same currency get the current subscriptions currency filter subscription choices 
            #that match the  tier and frequency and currency
            if choice.stripe_renewal_frequency == "month":
                cost_per_day_new_plan = (choice.price/30)
            elif choice.stripe_renewal_frequency == "year":
                cost_per_day_new_plan = (choice.price/365)
            print(cost_per_day_new_plan)
            days_left = int(total_value_of_days_left/cost_per_day_new_plan)
            context['remaining_days'] = True

        else:
            context['existing_higher_tier_subscription'] =True


        #round days down
        if days_left > 0:

            trial_period_days += days_left
        
    #Do the same for free trial days left
    # Need to convert? Decided not to convert and give user extra
    if user_payment_status.status == "free_trial":
        days_left = int((user_payment_status.subscription_expiry - current_time).days)
        if days_left > 0:
            trial_period_days += days_left
            context['remaining_days'] = True

    
    context['trial_period_days'] = trial_period_days






    try:
            # Create the subscription.
            # latest invoice and that invoice's payment_intent
            # so we can pass it to the front end to confirm the payment
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{
                    'price': price_id,
                }],
                trial_period_days= trial_period_days,
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent'],
            )
            subscription_id = subscription.id 

                
            if trial_period_days != 0:
                setup_intent = stripe.SetupIntent.create(
                customer=customer_id,
                payment_method_types=["card"],
                usage = 'off_session'

                )
                client_secret = setup_intent.client_secret
            else:
                client_secret = subscription.latest_invoice.payment_intent.client_secret



    except Exception as e:
        print("Exception occured")
        print(e)
        return HttpResponse("An error occurred, please try again later or contact us via email explaining the problem")
    
    
    return_url = request.build_absolute_uri(reverse('success', kwargs={'subscription_id': subscription_id}))
    
    #Created here so the stripe customer id is stored and not lost
    user_subscription = UserSubscriptions.objects.create(
        user_payment_status=user_payment_status,
        subscription_choice = choice,
        status = "created",
        stripe_customer_id = customer_id,
        subscription_id = subscription_id,
        next_due = datetime.utcfromtimestamp(subscription['current_period_end']),
        payment_method = "Stripe",
        amount_subscribed = price,
        renewal_frequency = choice.renewal_frequency,
        currency_code = "USD",
    )



    context['client_secret'] =  client_secret
    context['stripe_pub_key'] =  stripe_pub_key
    context['return_url'] =  return_url
    context['trial_period_days'] =  trial_period_days
    context['user_subscription'] = user_subscription


    
    return render(request, "includes/subscribe_modal_content.html", context=context)