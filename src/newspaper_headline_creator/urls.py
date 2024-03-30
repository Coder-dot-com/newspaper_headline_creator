"""
URL configuration for newspaper_headline_creator project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic.base import TemplateView #import TemplateView

from . import views

urlpatterns = [
    # path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),  

    path('admin/1a/SecureLog/', admin.site.urls),

    path("", views.home, name="home"),
    
    re_path("robots.txt\/?$",TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),  #add the robots.txt file

    path('privacy_policy/', views.privacy_policy, name="privacy_policy",),
    path('terms_and_conditions/', views.terms_and_conditions, name="terms_and_conditions",),


] 
