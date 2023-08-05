====================
Hadrian.Contrib.Auth
====================

Included in ``hadrian.contrib`` is ``hadrian.contrib.auth`` a authentication helper library.


Decorator Usage
===============

Load the decorator::

    from hadrian.contrib.auth.decorators import group_required
    
Place the decorator on a view function you want to protect::

    @group_required("Students")
    def view_something(request):
        return render()

Anyone who does not belong to the group ``Students`` will raise the PermissionDenied exception.


