from django.shortcuts import redirect, render, HttpResponse

from .models import UserEmail
from .forms import EmailForm
# Create your views here.



def subscribe_email(request):

    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            email_object = UserEmail.objects.get_or_create(email=email)[0]
            email_object.promo_consent = True
            email_object.save()

            return HttpResponse("<span class='text-center d-block'> Email signed up! </span>")
        else:
            return HttpResponse("Email is not valid")
        
    else:
        form = EmailForm()
        context = {'form': form}
        return render(request, 'home_site/includes/subscribe_email.html', context=context)

def unsubscribe_email(request):
    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            email_object = UserEmail.objects.filter(email=email)
            email_object.update(promo_consent=False)
            return HttpResponse("<span class='text-center d-block'> Email unsubscribed! </span>")

    else:
        form = EmailForm()
        context = {'form': form}
        return render(request, 'unsubscribe.html', context=context)