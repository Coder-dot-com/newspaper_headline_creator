from django.shortcuts import render

def home(request):


    return render(request, 'home_site/index.html')



def robots_txt(request):
    return render(request, 'robots.txt')

def privacy_policy(request):
    return render(request, 'home_site/privacy_policy.html')


def terms_and_conditions(request):
    return render(request, 'home_site/terms_and_conditions.html')

