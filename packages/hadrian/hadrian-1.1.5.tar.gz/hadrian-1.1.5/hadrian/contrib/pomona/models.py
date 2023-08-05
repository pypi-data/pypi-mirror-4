from django.db import models
from hadrian.contrib.pomona.choices import LEVEL_CHOICES


class Log(models.Model):
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return "%s - %s - %s" % (str(self.created), self.level, self.message)