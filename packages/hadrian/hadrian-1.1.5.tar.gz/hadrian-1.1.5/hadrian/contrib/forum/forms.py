from django import forms
from hadrian.contrib.forum.models import Topic


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        exclude = ('author', 'forum')