from django.shortcuts import render

# Create your views here.

def create_headline_form_htmx(request):
    return render(request, "includes/create_headline_form.html")


def submit_create_headline_form_htmx(request):
    print(request.POST)
    return render(request, "includes/headlines_response.html")