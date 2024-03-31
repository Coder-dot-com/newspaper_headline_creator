from django.shortcuts import render, HttpResponse, redirect
from .models import SubscriptionChoices, UserSubscriptions
from datetime import datetime, timezone, timedelta
import stripe
from product_launch_site.settings import STRIPE_PUBLIC_KEY, STRIPE_SECRET_KEY, STRIPE_ENDPOINT_SECRET
from django.contrib.auth.decorators import login_required
from tiers.models import UserTier, Tier
from ai.models import UserAI
from django.views.decorators.csrf import csrf_exempt
from .tasks import cancel_subscription
from .models import UserPaymentStatus
from django.contrib import messages
from django.db.models import Q
from emails.tasks import subscription_confirmed_email, subscription_cancelled_email

stripe.api_key = STRIPE_SECRET_KEY

stripe_pub_key = STRIPE_PUBLIC_KEY
 
# Create your views here.
def subscription_choices(request):

    subscription_choices = SubscriptionChoices.objects.all().order_by('tier__tier_ranking')
    context = {}
    context['subscription_choices'] = subscription_choices

    user_subscription_with_greater_tier = None

    if request.user.is_authenticated:
        user=request.user
        user_payment_status = UserPaymentStatus.objects.get(user=user)

        if user_payment_status.status == "active":
            #get the latest user subscription
            try:
                user_subscription = UserSubscriptions.objects.filter(Q(
                    user_payment_status=user_payment_status,
                    status="paid")).latest('created_at')
            except UserSubscriptions.DoesNotExist:
                try:
                    user_subscription = UserSubscriptions.objects.filter(
                user_payment_status=user_payment_status,
                status="cancelled", 
                ).latest('created_at')
                except:
                    user_subscription = ""
            context['user_subscription'] = user_subscription


        #todo: now need to ensure that user_payment status is synced and set properly/ create a new property to check this?
   
            try:
                # Check if higher tier cancelled subscription available
                user_subscription_with_greater_tier = UserSubscriptions.objects.filter(Q(
                                user_payment_status=user_payment_status,
                                status="cancelled"),
                                next_due__gt= datetime.now(timezone.utc) + timedelta(days=1),
                                subscription_choice__tier__tier_ranking__gt=user_subscription.subscription_choice.tier.tier_ranking).order_by((
                                    'subscription_choice__tier__tier_ranking')).reverse()[0]
                            
            except IndexError:
                pass

    context['user_subscription_with_greater_tier'] = user_subscription_with_greater_tier



    return render(request, "subscription_choices.html", context=context)



def _post_subscription_success(subscription_id=None, request=None, stripe_customer_id=None, webhook=False, event=""):
    print("POST SUBSCRIPTION SUCCESS")
    context = {}

    if not stripe_customer_id:

        user_subscription = UserSubscriptions.objects.get(subscription_id=subscription_id)
        stripe_customer_id = user_subscription.stripe_customer_id
    else:
        user_subscription = UserSubscriptions.objects.get(stripe_customer_id=stripe_customer_id)
    
    #get any existing user subscriptions of a greater tier thata re active
    user_payment_status = user_subscription.user_payment_status

    #set as default payment method

    try:
        customer_id = user_subscription.stripe_customer_id
        payment_method_id =  stripe.Customer.list_payment_methods(customer_id,limit=1,)['data'][0]['id']

        stripe.Customer.modify(customer_id, invoice_settings={'default_payment_method': payment_method_id})
    except IndexError:
        print(f"Index error setting stripe defualt payment method event: {event}")    




    #end set as defualt payment method


           # Check if higher tier cancelled subscription available
    try:
        user_subscription_with_greater_tier = UserSubscriptions.objects.filter(Q(
                            user_payment_status=user_payment_status,
                            status="cancelled"),
                            next_due__gt= datetime.now(timezone.utc) +timedelta(days=1),
                            subscription_choice__tier__tier_ranking__gt=user_subscription.subscription_choice.tier.tier_ranking).order_by((
                                'subscription_choice__tier__tier_ranking')).reverse()[0]  
    except:
        user_subscription_with_greater_tier = None   

    #only if this hasn't run already in case user refreshes the page 
    if not  user_subscription.status == "paid" and not user_subscription.status == "cancelled":

        subscriptions = stripe.Subscription.list(
        customer=stripe_customer_id,
        )
 
        subscription_id = (subscriptions['data'][0]['id'])
        user_subscription.subscription_id = subscription_id
        user_subscription.save()
        
        subscription_status_is_active = (subscriptions['data'][0]['items']['data'][0]['plan']['active'])

        if subscription_status_is_active == True:
            print("Active")
        
            next_payment_due = subscriptions['data'][0]['current_period_end']
            interval_start_date = subscriptions['data'][0]['current_period_start']

            
            #Use the subscription_id and customer_id to get the customer and the subscription
            user_subscription.status = "paid"
            user_subscription.next_due =  datetime.utcfromtimestamp(next_payment_due)
            user_subscription.latest_response = subscriptions
            user_subscription.interval_start_date = datetime.utcfromtimestamp(interval_start_date)
            user_subscription.save()
            if not user_subscription_with_greater_tier:
    
                user_payment_status.status = "active"
                user_payment_status.subscription_expiry = user_subscription.next_due
                user_payment_status.save()

                user=user_subscription.user_payment_status.user
                #update user tier
                user_tier = UserTier.objects.get(user=user)

                user_tier.tier = user_subscription.subscription_choice.tier

                user_tier.save()

                #set user monthly credits only run once
                user_ai = UserAI.objects.get(user=user)
                user_ai.monthly_ai_credits_remaining = user_tier.tier.monthly_ai_credits
                user_ai.save()


            

    

            #Check and Modify any other values required



        if webhook:
            try:                     
                subscription_confirmed_email.delay(subscription_id) 
                print("subscription confirm email scheduled")
            except Exception as e:
                print(e)


    context = {
            'user_subscription': user_subscription,
            }

    return context



@login_required
def success(request, subscription_id):
    user = request.user
    user_subscription = UserSubscriptions.objects.get(subscription_id=subscription_id)
    if user == user_subscription.user_payment_status.user:
        context = _post_subscription_success(subscription_id=subscription_id, request=request)
        user_subscription = context['user_subscription']
        if user_subscription.status == "cancelled":
            return redirect('dashboard_home')
        return render(request, 'thank_you.html', context=context)
    else:
        return redirect('login_user')



#Verify payment succeeded and create payment object
@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = STRIPE_SECRET_KEY
    endpoint_secret = STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        print(e)
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print(e)
        # Invalid signature
        return HttpResponse(status=400)


    event_type = event['type']
    print('event_type', event_type)
    
    if event_type == 'setup_intent.succeeded':
        customer_id = event['data']['object']['customer']
        _post_subscription_success(stripe_customer_id=customer_id, webhook=True, event="setup_intent.succeeded")
    
    elif event_type == 'payment_intent.succeeded':
        customer_id = event['data']['object']['customer']
        _post_subscription_success(stripe_customer_id=customer_id, webhook=True, event="setup_intent.succeeded")        #add check to see if event


    elif event_type == 'invoice.paid':
        # Used to provision services after the trial has ended.
        # The status of the invoice will show up as paid. Store the status in your
        # database to reference when a user accesses your service to avoid hitting rate
        # limits.
        customer_id = event['data']['object']['customer']
        print(event)
        if event['data']['object']['amount_due']:
            _post_subscription_success(stripe_customer_id=customer_id, event="invoice.paid")

    elif event_type == 'invoice.payment_failed':
        # If the payment fails or the customer does not have a valid payment method,
        # an invoice.payment_failed event is sent, the subscription becomes past_due.
        # Use this webhook to notify your user that their payment has
        # failed and to retrieve new card details.
        customer_id = event['data']['object']['customer']

        user_subscription = UserSubscriptions.objects.get(stripe_customer_id=customer_id)
        user_payment_status_id = user_subscription.user_payment_status.id

        cancel_subscription.delay(user_payment_status_id)
        subscription_cancelled_email.delay(user_subscription.subscription_id, True)



    elif event_type == 'customer.subscription.deleted':
        pass
        # handle subscription canceled automatically based
        # upon your subscription settings. Or if the user cancels it.

    return HttpResponse(status=200)





@login_required
def cancel_subscription_view(request):
    
    #Use the stripe method Cancel subscription at billing end
    user=request.user
    user_payment_status = UserPaymentStatus.objects.get(user=user)
    
    user_subscription = UserSubscriptions.objects.get(user_payment_status=user_payment_status, status="paid")

    stripe_subscription_id = user_subscription.subscription_id
    #Use the stripe method Cancel subscription at billing end
    
    try:
        stripe.Subscription.modify(
        stripe_subscription_id,
        cancel_at_period_end=True
        )

        #Thrn update all values
        user_subscription.status = "cancelled"
        user_subscription.save()

        messages.success(request, "Subscription successfully cancelled")

        subscription_cancelled_email.delay(user_subscription.subscription_id)

    except Exception as e:
        messages.error(request, "An error occured when cancelling the subscription")

        print(e)
    return redirect('subscription_choices')




  