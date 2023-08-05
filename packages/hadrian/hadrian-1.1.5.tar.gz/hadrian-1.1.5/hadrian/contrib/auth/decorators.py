from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def group_required(group_name, login_url=None):
    """Ensures a user is a memeber of group_name.  Throws 403 exception if not."""
    def in_groups(u):
        if u.is_authenticated():
            if bool(u.groups.filter(name=group_name)) | u.is_superuser:
                return True
        raise PermissionDenied
    return user_passes_test(in_groups, login_url)