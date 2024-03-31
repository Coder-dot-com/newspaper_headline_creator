from django.shortcuts import render, HttpResponse
from .models import HeadlineRequest
from .tasks import create_headlines_celery
from emails.models import UserEmail
# Create your views here.


def submit_create_headline_form_htmx(request):
    print(request.POST)
    article = request.POST['article']
    tone = request.POST['tone']

    session_id = request.session.session_key
    if not session_id:
        request.session.save()
        session_id = request.session.session_key



    headline_request_object = HeadlineRequest.objects.create(session_id=session_id, input_phrase=article, tone=tone)

    create_headlines_celery.delay(session_id, headline_request_object.unique_id)

    context = {
        'submitted': True,
        'headline_request_object': headline_request_object,


    }
    return render(request, "includes/headlines_response.html", context=context)


def poll_create_headline_form_htmx(request, uuid):
    #

    session_id = request.session.session_key
    if not session_id:
        request.session.save()
        session_id = request.session.session_key

    try:
        headline_request_object = HeadlineRequest.objects.get(session_id=session_id, unique_id=uuid)

        context = {
            'headline_request_object': headline_request_object,

        }

        if not headline_request_object.response:
            context['submitted'] = True

        return render(request, "includes/headlines_response.html", context=context)
    
    except HeadlineRequest.DoesNotExist: 
        pass



def capture_email_headline_generator_htmx(request, uuid):

    session_id = request.session.session_key
    if not session_id:
        request.session.save()
        session_id = request.session.session_key

    try:
        headline_request_object = HeadlineRequest.objects.get(session_id=session_id, unique_id=uuid)

    except HeadlineRequest.DoesNotExist:
        return HttpResponse("An error occured")
    
    email = request.POST['email']

    email, created = UserEmail.objects.get_or_create(email=email, promo_consent=True)
    headline_request_object.email = email
    headline_request_object.save()
    context = {
            'headline_request_object': headline_request_object,
            'email': email,

        }



    return render(request, "includes/headlines_response.html", context=context)