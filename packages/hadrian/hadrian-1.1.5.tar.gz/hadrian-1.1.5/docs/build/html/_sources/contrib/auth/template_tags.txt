=============
Template Tags
=============

If User Group
-------------

``ifusergroup`` Checks to see if the user belongs to a certain user group.

    {% load group_auth %}

    {% ifusergroup Something %}

    <!-- Do something only Something can do -->

    {% endifusergroup %}

Additionally, you must have the auth package in your installed apps.

    hadrian.contrib.auth