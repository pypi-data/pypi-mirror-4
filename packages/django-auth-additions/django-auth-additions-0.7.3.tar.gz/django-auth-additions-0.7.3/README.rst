django-auth-additions
======================

Adds some bits that help make django.contrib.auth a bit more useful.

Group gains a 'rank' field, that can be used to rank groups (useful where
groups need to be able to be limited to view only groups 'lower' than
they are).

Group gains a .duplicate() method, that will duplicate a group, including
all of it's permissions.

User gains methods for custom permissions:
   * can_view(object)
   * can_edit(object)
   * can_delete(object)
   * can_create(class)

These will use the current permissions, but also allow for methods to be
added on the object/class being tested, which can permit or deny access
according to custom rules.  I use this for instance to only allow staff
to view other staff who work at the same location(s).

Future:
* Configure using data from ``DJANGO_SETTINGS_MODULE``
* Unique email addresses
* Non-nullable email
* Index on email
* Random username on save (or email?)
* email in template (?)
