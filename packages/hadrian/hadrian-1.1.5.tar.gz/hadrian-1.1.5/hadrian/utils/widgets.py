from django import forms
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe


class ShowFileWidget(forms.FileInput):
    """
A FileField Widget that shows its current value if it has one.
"""
    def __init__(self, attrs={}):
        super(ShowFileWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        if value and hasattr(value, "url"):
            output.append('%s <a target="_blank" href="%s">%s</a> <br />%s ' % \
                (_('Currently:'), value.url, value, _('Change:')))
        output.append(super(ShowFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))