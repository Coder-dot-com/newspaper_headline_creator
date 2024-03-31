"""mem_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import  path, include
from . import views, views_htmx

urlpatterns = [
    path('subscription_choices/', views.subscription_choices, name="subscription_choices",),
    path('subscribe_modal_htmx/<choice_id>/', views_htmx.subscribe_modal_htmx, name="subscribe_modal_htmx",),
    path('success/<subscription_id>/', views.success, name="success",),
    path('webhook/', views.stripe_webhook, name="stripe_webhook"),
    path('cancel_subscription/', views.cancel_subscription_view, name="cancel_subscription",),

]
