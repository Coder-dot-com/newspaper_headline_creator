from django.contrib import admin

from emails.models import SentEmail, UserEmail

# Register your models here.
class UserEmailAdmin(admin.ModelAdmin):
    list_display = ['email',  'promo_consent', 'date_time_added']


admin.site.register(SentEmail)
admin.site.register(UserEmail, UserEmailAdmin)