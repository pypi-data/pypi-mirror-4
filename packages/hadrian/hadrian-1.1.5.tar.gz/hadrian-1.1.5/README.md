[![Build Status](https://secure.travis-ci.org/dstegelman/hadrian.png?branch=develop)](http://travis-ci.org/dstegelman/hadrian)

What?!
======

Hadrian - A collection of plugable Django apps and utilities that I use in my projects.  I find these apps and scripts useful, either use it or don't.


Utilties/Apps
=============

* ISO Country Choices
* Gravatar library/template tags
* Starter fabric file
* Unique_slugify utiltiy
* File field widget that displays the currently uploaded file
* Middleware to require login on every page
* Custom tagging application that uses slugs (Deprecated, use django-taggit instead)

Installation
============

    pip install hadrian


Want to use the gravatar template tags?

* Add hadrian.contrib.gravatar to installed apps
* load gravatar_tags
* Call get_gravatar or show_gravatar ( Get is just the image URL, while show provides the img tag wrapper )


Use it or don't.

Hadrian (Latin: Publius Aelius Trajanus Hadrianus Augustus 24 January 76 – 10 July 138), commonly known as Hadrian and after his apotheosis Divus Hadrianus, was Roman Emperor from 117 to 138. He is best known for building Hadrian's Wall, which marked the northern limit of Roman territory in Britain. In Rome, he re-built the Pantheon and constructed the Temple of Venus and Roma. In addition to being emperor, Hadrian was a humanist and was philhellene in all his tastes. He was the third of the so-called Five Good Emperors.