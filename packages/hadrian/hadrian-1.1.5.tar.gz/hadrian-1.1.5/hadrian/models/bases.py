from django.db import models

class AuditBase(models.Model):
    # Audit Fields
    created_on = models.DateField(auto_now_add=True, blank=True, null=True, editable=False)
    updated_on = models.DateField(auto_now=True, blank=True, null=True, editable=False)

    class Meta:
        abstract = True
