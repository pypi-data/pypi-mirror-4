from django import forms
from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from django.contrib import admin
from django.contrib import auth
from django.contrib import messages

from auth_additions.forms import UserChangeForm
from admin_additions.patchers import add_actions, patch_admin

#####################
#                   #
#  Group additions  #
#                   #
#####################

# Add a duplicate... action to the Group admin.


class DuplicateGroupForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    new_name = forms.CharField()
    
def duplicate_group(self, request, queryset):
    form = None
    
    if queryset.count() != 1:
        messages.error(request,
            "You may only duplicate one group at a time."
        )
        return HttpResponseRedirect(request.get_full_path())
    
    if 'apply' in request.POST:
        form = DuplicateGroupForm(request.POST)
        
        if form.is_valid():
            name = form.cleaned_data['new_name']
                        
            group = queryset.get()
            
            group.duplicate(name)
            
            self.message_user(request, "Duplicated group %s as %s" % (
                group.name, name
            ))
            return HttpResponseRedirect(request.get_full_path())
    
    if not form:
        form = DuplicateGroupForm(initial={
            "_selected_action": request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        })
        
    return direct_to_template(request, 'admin/auth/duplicate_group.html', {
        'queryset': queryset,
        'obj': queryset.get(),
        'form': form,
    })

duplicate_group.short_description = "Duplicate a group, including all permissions"

add_actions(auth.models.Group, duplicate_group)

#####################
#                   #
#  User additions   #
#                   #
#####################

# Patch in the custom form we have.
@patch_admin(auth.models.User)
def update_form(model_admin):
    model_admin.form = UserChangeForm
