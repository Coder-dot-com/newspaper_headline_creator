from django.db import models

from django.contrib.auth import get_user_model
from datetime import timedelta, datetime, timezone

User = get_user_model()



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='profile')
    email_confirmed = models.BooleanField(default=False) 
    reset_password = models.BooleanField(default=False)







