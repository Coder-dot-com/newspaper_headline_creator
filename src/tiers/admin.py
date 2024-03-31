from django.contrib import admin

from .models import Tier, UserTier

# Register your models here.

class TierAdmin(admin.ModelAdmin):
    list_display = ['type',  'display_name', 'tier_ranking']


admin.site.register(Tier, TierAdmin)

admin.site.register(UserTier)