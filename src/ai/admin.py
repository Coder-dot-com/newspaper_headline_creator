from django.contrib import admin
from .models import HeadlineRequest


# Register your models here.
class HeadlineRequestAdmin(admin.ModelAdmin):
    list_display = ['email', 'input_phrase', 'tone', 'time_created' ]


admin.site.register(HeadlineRequest, HeadlineRequestAdmin)