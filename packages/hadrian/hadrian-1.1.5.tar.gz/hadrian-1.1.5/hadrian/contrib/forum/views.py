from hadrian.contrib.forum.models import *
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from hadrian.contrib.forum.forms import *

def home(request):
    forums = Forum.objects.all()
    context = {'forums': forums}
    return render(request, 'forum/home.html', context)
    
def topic(request, forum_slug, topic_slug):
    topic = get_object_or_404(Topic, slug=topic_slug)
    context = {'topic': topic}
    return render(request, 'forum/topic.html', context)
    
def forum(request, forum_slug):
    forum = get_object_or_404(Forum, slug=forum_slug)
    topics = Topic.objects.filter(forum__slug=forum_slug)
    context = {'forum': forum, 'topics': topics}
    return render(request, 'forum/forum.html', context)
    
# Forms
@login_required
def new_topic(request, forum_slug):
    context = {}
    if request.method == "POST":
        form = TopicForm(request.POST)
        
    else:
        form = TopicForm()
        context['form'] = form
    return render(request, 'forum/forms/add_topic.html', context)
