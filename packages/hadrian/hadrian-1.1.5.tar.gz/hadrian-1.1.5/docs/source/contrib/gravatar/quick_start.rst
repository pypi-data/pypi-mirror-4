========================
Hadrian.Contrib.Gravatar
========================

Included in ``hadrian.contrib`` is ``hadrian.contrib.gravatar`` a gravatar template tag library.


Setup
=====

Add ``hadrian.contrib.gravatar`` to installed apps.

Usage
=====

Load the gravatar tag library in your template::

    {% load gravatar_tags %}

Getting just the URL of the image::

     <img src="{% get_gravatar email_address 75 %}" width="75">
     
Using the built in wrapper::

    {% gravatar email_address 75 %}
    
Which produces::

    <img src="{{ gravatar.url }}"
        width="{{ gravatar.size }}" height="{{ gravatar.size }}" border="0" class="avatar" />
