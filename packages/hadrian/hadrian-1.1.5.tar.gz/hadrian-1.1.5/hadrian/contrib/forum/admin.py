from django.contrib import admin
from hadrian.contrib.forum.models import *


admin.site.register(Forum)
admin.site.register(Board)
admin.site.register(Topic)
admin.site.register(Reply)