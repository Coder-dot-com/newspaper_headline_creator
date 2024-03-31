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
from django.urls import path

from . import views, views_htmx

urlpatterns = [
    
    path("create_headline_form_htmx", views_htmx.create_headline_form_htmx, name="create_headline_form_htmx"),
    path("submit_create_headline_form_htmx", views_htmx.submit_create_headline_form_htmx, name="submit_create_headline_form_htmx"),




] 
