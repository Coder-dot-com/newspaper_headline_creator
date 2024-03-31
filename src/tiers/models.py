from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()
# Create your models here.

tier_choices = (
    ('free_tier', 'free_tier'),
    ('professional', 'professional'),
    ('business', 'business'),
    ('enterprise', 'enterprise'),


)


class Tier(models.Model):
    type = models.CharField(choices=tier_choices, unique=True, max_length=200)
    display_name = models.CharField(max_length=200)
    tier_ranking = models.IntegerField(unique=True)
    badge_color = models.CharField(max_length=50, null=True, blank=True)

    monthly_ai_credits = models.IntegerField(default=5)
    monthly_ai_credits_last_set = models.DateTimeField()

    who_for = models.TextField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.display_name
    


class UserTier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tier = models.ForeignKey(Tier, on_delete=models.PROTECT)

