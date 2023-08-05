from django.contrib import admin
from hadrian.dist.tagging.models import Tag, TaggedItem
from hadrian.dist.tagging.forms import TagAdminForm

class TagAdmin(admin.ModelAdmin):
    form = TagAdminForm

admin.site.register(TaggedItem)
admin.site.register(Tag, TagAdmin)




