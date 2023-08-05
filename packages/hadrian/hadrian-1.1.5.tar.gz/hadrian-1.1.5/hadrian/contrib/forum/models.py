from django.db import models
from django.contrib.auth.models import User
from hadrian.utils.slugs import unique_slugify

class Board(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    
    def __unicode__(self):
        return self.title
    
    
class Forum(models.Model):
    board = models.ForeignKey(Board)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(editable=False)
    
    def __unicode__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        unique_slugify(self, self.title)
        super(Forum, self).save(*args, **kwargs)
    
    @models.permalink
    def get_absolute_url(self):
        return ('hadrian.contrib.forum.views.forum', (), {'forum_slug': self.slug})
    
class Topic(models.Model):
    forum = models.ForeignKey(Forum)
    title = models.CharField(max_length=200)
    author = models.ForeignKey(User)
    date_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    content = models.TextField(blank=True, null=True)
    sticky = models.BooleanField(default=False)
    slug = models.SlugField(editable=False)
    
    def __unicode__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        unique_slugify(self, self.title)
        super(Topic, self).save(*args, **kwargs)
        
    
    @models.permalink
    def get_absolute_url(self):
        return ('hadrian.contrib.forum.views.topic', (), {'forum_slug': self.forum.slug, 'topic_slug': self.slug})
    
    
class Reply(models.Model):
    topic = models.ForeignKey(Topic)
    author = models.ForeignKey(User)
    date_created = models.DateTimeField(auto_now=False, auto_now_add=True)
    content = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        return self.content
    
    