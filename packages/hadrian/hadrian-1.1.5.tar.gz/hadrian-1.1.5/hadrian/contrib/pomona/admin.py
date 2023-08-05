from django.contrib import admin
from hadrian.contrib.pomona.models import Log

class LogAdmin(admin.ModelAdmin):
    list_display = ('level', 'message', 'created')
    
admin.site.register(Log, LogAdmin)