from functools import wraps

from django.core.exceptions import PermissionDenied

def superuser_required(view_func):
    """ Decorator for requiring a super
    user """
    
    @wraps(view_func)
    def _checklogin(request, *args, **kwargs):
        if request.user.is_active and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            return PermissionDenied
    return _checklogin
