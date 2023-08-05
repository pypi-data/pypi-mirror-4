from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.exceptions import PermissionDenied, ImproperlyConfigured

__author__ = "Derek Stegelman"

class LoginRequiredMixin(object):
    """
    View mixin for requiring a Login.
    """

    login_url = settings.LOGIN_URL

    @method_decorator(login_required(login_url=login_url))
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)

class SuperUserRequiredMixin(object):
    """
    Require a logged in Superuser
    """
    
    login_url = settings.LOGIN_URL
    
    @method_decorator(login_required(login_url=login_url))
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied

        return super(SuperUserRequiredMixin, self).dispatch(request, *args, **kwargs)

class StaffRequiredMixin(object):
    """
    Require a logged in Staff member.
    """
    
    login_url = settings.LOGIN_URL

    @method_decorator(login_required(login_url=login_url))
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied

        return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)


class GroupRequiredMixin(object):
    """
    View mixin which verifies that the logged in user has the specified
    Group.

    Make sure to use the LoginRequiredMixin ahead of this.

    Raises a 403 Permission Denied Error.

    """
    
    login_url = settings.LOGIN_URL
    group = None

    @method_decorator(login_required(login_url=login_url))
    def dispatch(self, request, *args, **kwargs):
        if not self.group:
            raise ImproperlyConfigured("No group provided.")

        if not bool(request.user.groups.filter(name=self.group)):
            raise PermissionDenied

        return super(GroupRequiredMixin, self).dispatch(request,
            *args, **kwargs)
            
class PermissionRequiredMixin(object):
    """
    Original work by Kenneth Love and Chris Jones

    Modifed to use django 403 Permission Denied Exception

    View mixin which verifies that the logged in user has the specified
    permission.

    Class Settings
    `permission_required` - the permission to check for.
    `login_url` - the login url of site
    `redirect_field_name` - defaults to "next"
    `raise_exception` - defaults to False - raise 403 if set to True

    Example Usage

        class SomeView(PermissionRequiredMixin, ListView):
            ...
            # required
            permission_required = "app.permission"

            # optional
            login_url = "/signup/"
            redirect_field_name = "hollaback"
            raise_exception = True
            ...
    """
    login_url = settings.LOGIN_URL  # LOGIN_URL from project settings
    permission_required = None  # Default required perms to none

    def dispatch(self, request, *args, **kwargs):
        # Make sure that a permission_required is set on the view,
        # and if it is, that it only has two parts (app.action_model)
        # or raise a configuration error.
        if self.permission_required == None or len(
            self.permission_required.split(".")) != 2:
            raise ImproperlyConfigured("'PermissionRequiredMixin' requires "
                                       "'permission_required' attribute to be set.")

        # Check to see if the request's user has the required permission.
        has_permission = request.user.has_perm(self.permission_required)

        if not has_permission:  # If the user lacks the permission
            raise PermissionDenied

        return super(PermissionRequiredMixin, self).dispatch(request,
            *args, **kwargs)