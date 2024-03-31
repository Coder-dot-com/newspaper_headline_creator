from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model() 
# Create your models here.

class UserAI(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    monthly_ai_credits_remaining = models.IntegerField(default=5)
    purchased_ai_credits_remaining = models.IntegerField(default=0)

    
class HeadlineRequest(models.Model):
    user_ai = models.ForeignKey(UserAI, on_delete=models.CASCADE, null=True, blank=True)
    session_id  = models.CharField(max_length=1000, null=True, blank=True)
    unique_id = models.UUIDField(default = uuid.uuid4,) 
    input_phrase = models.TextField(max_length=10000)
    tone = models.CharField(max_length=200)
    time_created = models.DateTimeField(auto_now_add=True)
    response = models.TextField(max_length=10000, null=True, blank=True)

    def get_list_of_headlines(self):
        if self.response:
            return self.response.split('<br>')