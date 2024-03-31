from django.urls.conf import path
from . import views

urlpatterns = [
    path('unsubscribe_email/', views.unsubscribe_email, name='unsubscribe_email'),
    path('subscribe_email/', views.subscribe_email, name='subscribe_email'),

]