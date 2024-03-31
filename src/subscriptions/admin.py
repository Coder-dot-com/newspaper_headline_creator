from django.contrib import admin

# Register your models here.
from subscriptions.models import SubscriptionChoices, UserPaymentStatus, UserSubscriptions

# Register your models here.



class SubscriptionChoiceAdmin(admin.ModelAdmin):
    list_display = ['tier',  'renewal_frequency', 'price', 'stripe_price_id',  'subscription_name']


admin.site.register(UserPaymentStatus)
admin.site.register(UserSubscriptions)

admin.site.register(SubscriptionChoices, SubscriptionChoiceAdmin)