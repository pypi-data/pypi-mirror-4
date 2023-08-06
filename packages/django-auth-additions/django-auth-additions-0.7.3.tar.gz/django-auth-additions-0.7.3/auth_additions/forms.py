from django.contrib.auth.forms import authenticate, UserChangeForm
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django import forms

class ExistingUserForm(forms.Form):
    """
    This form is used by the socialauth stuff.
    """
    username = forms.CharField()
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    
    def __init__(self, user, profile, *args, **kwargs):
        super(ExistingUserForm, self).__init__(*args, **kwargs)
        self.user = user
        self.profile = profile
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user = authenticate(username=username, password=password)
            if self.user is None:
                raise forms.ValidationError(_("Please enter a correct username and password. Note that both fields are case-sensitive."))
            elif not self.user.is_active:
                raise forms.ValidationError(_("This account is inactive."))

        return self.cleaned_data
        
    def save(self, request=None):
        self.profile.user = self.user
        self.profile.save()
        return self.user
    
    @property
    def profile_name(self):
        return self.profile.__class__.__name__.replace('Profile', '')

# Extend the UserChangeForm to allow for the correct number of characters.
USERNAME_LENGTH = User._meta.get_field_by_name('username')[0].max_length

class UserEmailUniqueMixin(object):
    """
    Mixin this class if you require all email addresses (across all
    sub-classes of User) to be unique.
    """
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.exclude(pk=self.instance.pk).filter(email=email, is_active=True).exists():
            raise forms.ValidationError("That email address is in use. You may use <something>+email@example.com")
        return email

class UserChangeForm(UserChangeForm):
    username = forms.RegexField(
        label=_(u"Username"),
        max_length=USERNAME_LENGTH,
        regex=r"^[\w .@+-]+$",
        required=False,
        help_text = _("Optional. %s characters or fewer. Letters, digits and "
                      "@/ /./+/-/_ only." % USERNAME_LENGTH),
        error_messages = {
            'invalid': _("This value may contain only letters, numbers and "
                         "@/ /./+/-/_ characters.")}
    )
