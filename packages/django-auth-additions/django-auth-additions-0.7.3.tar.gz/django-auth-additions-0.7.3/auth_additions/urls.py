from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('')

try:
    if 'socialregistration' in settings.INSTALLED_APPS:
        if settings.SOCIALREGISTRATION_NO_REGISTER:
            import forms
            urlpatterns += patterns('',
                url(r'^setup/$', 'socialregistration.views.setup',
                    {'form_class': forms.ExistingUserForm},
                ),
            )
except KeyError:
    pass