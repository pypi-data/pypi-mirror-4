Django Infuse
=============

Series of Class based mixins.  Requires Django 1.4s use of PermissionDenied exception. 

Installation
------------

    pip install django-infuse
    
Currently Supported Mixins
--------------------------

* Permission Required
* Staff Required
* Super User required
* Login Required
* Group Required

Usage
-----

### Login Required Mixin

Inherit the mixin you want to use and add any additional (optional) params.

	from infuse.auth.permissions import LoginRequiredMixin

	class MyLoginProtectedView(LoginRequiredMixin, ListView):
		# If login_url is not the url you want to redirect
		# users to, set one here.

		login_url = "/my/new/url/"

		# Do the rest of your stuff.....

### Group Required Mixin

The only other different one is GroupRequiredMixin

	from infuse.auth.permissions import GroupRequiredMixin

	class MyGroupRequiredView(GroupRequiredMixin, ListView):
		# Uses login_required, so you can optionally pass in
		# a url just like LoginRequired.

		# You MUST set a group, Infuse will throw an exception
		# if you do not.

		group = "My Awesome Group"


### Permission Required Mixin

Original work by Kenneth Love and Chris Jones.  Modified to always raise PermissionDenied

	from infuse.auth.permissions import PermissionRequiredMixin

	class PermissionRequiredView(PermissionRequiredMixin, ListView):
		# Permission to require
		permssion_required = 'model.can_do_something'
		
### What is Next?

* Wizard Mixin Helpers

