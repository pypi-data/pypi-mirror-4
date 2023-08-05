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
		

### Save and Continue Form Wizard

This mixin is still very much in a alpha status.  The django form wizard does not support the concept of 'Finish Later' or any
built in ability to save the form 'half done'.  This mixin provides a way for developers to add a 'Finish Later' functionality 
to their form wizard.

In order to use the 'Finish Later' functionality you must add a button/input element on your form wizard templates and name it 'save_only'

    <input type='submit' name='save_only' value='Finish Later'>
    
Next inherit the SaveAndContinue Mixin

    from infuse.wizard.mixins import SaveAndContinueWizard
    
    class MyFinishLaterWizard(SaveAndContinueWizard):
    
        # This url is where the user will be redirected to when 
        # they click the 'Finish Later' button
        save_only_url = reverse_lazy('wheretogowhenuserssaves')
    
In addition to the ``save_only_url`` that you are required to set, you may also provide the following methods:

    def post_save_only(self):
            pass
    
    def process_wizard_goto_step(self, wizard_goto_step):
        if wizard_goto_step and wizard_goto_step in self.get_form_list():
            self.storage.current_step = wizard_goto_step
            form = self.get_form(
                data=self.storage.get_step_data(self.steps.current),
                files=self.storage.get_step_files(self.steps.current))
            return self.render(form)
    
    def pre_process(self, form):
        pass

    def additional_file_processing(self):
        pass

    
* ``post_save_only`` - Called when save_only is executed.  Provides a way to hook into the save_only processor
* ``pre_process`` - Do any pre processing before forms are attempted to save.  Can be used to setup formsets.
* ``additional_file_processing`` - Do any additional file processing.  I use this to make sure that files saved to AWS are saved 
with the correct file name.
* ``process_wizard_goto_step`` - Allows you to override the default behaviour of going between steps.

This particular mixin is extreamly powerful, but is in a constantly changing state.  If you are using it, please provide some feedback of how and what your using it for, as well as any improvements you have.
 
    



