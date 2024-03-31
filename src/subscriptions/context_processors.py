from .models import UserPaymentStatus

def get_user_payment_status(request):

    if request.user.is_authenticated:
        try:
            user_payment_status = UserPaymentStatus.objects.get(user=request.user)
            user_payment_status.sync_subscription_expiry_model_method()

        except UserPaymentStatus.DoesNotExist:
            user_payment_status = None

    else:
        user_payment_status = None

    return dict(user_payment_status=user_payment_status)