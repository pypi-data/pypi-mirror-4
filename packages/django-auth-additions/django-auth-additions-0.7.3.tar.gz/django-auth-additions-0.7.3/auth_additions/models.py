from functools import wraps

from django.core.exceptions import ValidationError
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.core.validators import MaxLengthValidator

#####################
#                   #
#  Group additions  #
#                   #
#####################

# Groups need a ranking system.  Groups with a higher rank can be used to
# allow managers to see staff details, but not other managers (of the same
# rank, for instance).

try:
    Group._meta.get_field_by_name('rank')
except models.FieldDoesNotExist:
    Group.add_to_class('rank', models.PositiveSmallIntegerField(default=5))

# Ability to duplicate group, with all the same permissions.

def duplicate_group(group, new_name):
    """
    Duplicate a group, and all of it's permissions.
    Give it the provided name.
    
    Note: changing the original group's permission set will not update
    the duplicate group's permissions.
    """
    new_group = Group(name=new_name, rank=group.rank)
    new_group.save()
    new_group.permissions.add(*group.permissions.all())
    return new_group
    
Group.add_to_class('duplicate', duplicate_group)


#####################
#                   #
#  User additions   #
#                   #
#####################

# We can implement object-level permissions using the following method:
# 
# Put methods with the names 'viewable_by', 'editable_by' and 'deletable_by'
# onto your class that will be tested for those tasks.
# 
# A User object patched using the function below (and the four patches
# that follow) will be able to view/edit/delete/add objects of that class
# according to the method result.
# 
# If you pass in a class, instead of the object, it will only use the
# django permissions, rather than the method.
# 
# If the desired method cannot be found, it will revert back to the 
# django permission.
#
# If a django permission cannot be found, the method has_perm(None) will 
# result in the object being visible to all people.

def can_do(*tasks):
    
    def inner(user, obj_or_class, data=None):
        for task in tasks:
            # If the object we are looking at has a bound method %sable_by, then
            # we want to call that.
            if hasattr(obj_or_class, "%sable_by" % task):
                function = getattr(obj_or_class, "%sable_by" % task)
                if function.im_self:
                    if data:
                        return function(user, data)
                    return function(user)
            # Get the permission object that matches.
            if hasattr(obj_or_class._meta, 'get_%s_permission' % task):
                perm_name = getattr(obj_or_class._meta, 'get_%s_permission' % task)()
                if perm_name:
                    perm = '%s.%s' % (
                        obj_or_class._meta.app_label, 
                        perm_name
                    )
                    return user.has_perm(perm)
        # If we could not find any matching permissions, then the user may do it.
        return True
    return inner

User.add_to_class('can_view', can_do('read', 'view'))
User.add_to_class('can_edit', can_do('edit', 'change', 'update'))
User.add_to_class('can_delete', can_do('remove', 'delete'))
User.add_to_class('can_create', can_do('create', 'add'))


User.add_to_class('name', property(lambda x: x.get_full_name()))


### Patches to existing columns.

def increase_field_length(field, length):
    if field.max_length < length:
        field.max_length = length
        for v in field.validators:
            if isinstance(v, MaxLengthValidator):
                v.limit_value = length

# Change name/username/email length(s) to 128.
for f_name in ('first_name', 'last_name', 'email', 'username'):
    field = User._meta.get_field_by_name(f_name)[0]
    increase_field_length(field, 128)

# Make email address unique
# field = User._meta.get_field_by_name('email')[0]
# field._unique = True
# field.default = None
# field.null = True

# Allow nullable username
# field = User._meta.get_field_by_name('username')[0]
# field.default = None
# field.null = True

# @receiver(models.signals.pre_save, sender=User)
# def User_pre_save(sender, instance, **kwargs):
#     """
#     Ensure that email is unique.
#     Nullify blank usernames.
#     """
#     if instance.username == "":
#         instance.username = None
#     if sender.objects.filter(email=instance.email).exclude(pk=instance.pk).exclude(email=None).exists():
#         raise ValidationError(_("Email must be unique"))


# Change the default represention of a User to contain fullname, and email/username.

def User__unicode(self):
    return "%s %s <%s>" % (self.first_name, self.last_name, self.email or self.username)
User.__unicode__ = User__unicode


# Add a queryset method that will allow for
#
#       User.objects.with_permissions('foo.bar')
#

class PermissionFilterMixin:
    def with_permissions(self, *permission_names):
        """
        Filter the queryset of Users so that only those that would
        pass the 'has_perm' test for _all_ Permissions described by
        *permission_names are included.
        
        This would be all superusers, Users who have the Permissions
        directly, or Users who are a members of Groups that between them
        all have the Permissions.
        
        That is, if they have one Permission directly, another by virtue
        of being in a Group, and the rest by virtue of being in another
        Group, they would match.
        
        If they do not have _all_ of the Permissions, then they are
        removed from the queryset.
        """
        permission_filters = models.Q(pk=None)
        
        for permission_name in permission_names:
            app_label, codename = permission_name.split('.')
            permission_filters = permission_filters | models.Q(content_type__app_label=app_label, codename=codename)
        
        permissions = Permission.objects.filter(permission_filters)

        superuser_filter = models.Q(is_superuser=True)
        
        if len(permissions) != len(permission_names):
            return self.filter(superuser_filter).distinct()

        perm_filter = models.Q()
        
        for perm in permissions:
            groups_filter = models.Q(groups__in=perm.group_set.all())
            user_filter = models.Q(pk__in=perm.user_set.values_list('pk', flat=True))
            perm_filter = perm_filter & (groups_filter | user_filter)
        
        return self.filter(superuser_filter | perm_filter ).distinct()

# Queryset method for active users
class ActiveMixin:
    def active(self):
        return self.filter(is_active=True)

UserQuerySet = User.objects.all().__class__
UserQuerySet.__bases__ = (PermissionFilterMixin, ActiveMixin) + UserQuerySet.__bases__


#############################
#                           #
#  Permission additions    #
#                           #
#############################

field = Permission._meta.get_field_by_name('name')[0]
increase_field_length(field, 128)


def users_with_permission(self):
    """
    Return all Users who have this Permission.
    
    This will be all Users who are a member of a Group that has this
    Permission, Users who have this permission directly, or Users
    who have is_superuser=True.
    """
    groups_filter = models.Q(groups__in=self.group_set.all())
    user_filter = models.Q(pk__in=self.user_set.values_list('pk', flat=True))
    superuser_filter = models.Q(is_superuser=True)
    
    return User.objects.filter(user_filter | groups_filter | superuser_filter).distinct()

Permission.users_with_permission = users_with_permission
