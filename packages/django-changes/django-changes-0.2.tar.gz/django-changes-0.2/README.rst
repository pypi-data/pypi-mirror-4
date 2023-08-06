==============
django-changes
==============

A utility to store and access information about changes on objects in a Django
project.


Installation
============

``pip install django-changes``

Add to your Python path or ``setup.py install`` and add ``'changes'`` to your
``INSTALLED_APPS`` setting.


Usage
=====

You can use by importing the helper::

    from changes import changes
    # ...
    changes.add_change(someobj, who=request.user)

Or by using the object directly::

    from changes.models import Change
    # ...
    Change.objects.add_change_for_object(someobj, why='Because')


To get a queryset of changes that were added for an objects::

    changes.get_changes_for(someobj)

or::

    Change.objects.get_changes_for_object(someobj)


To get a queryset of changes that were made by a user::

    changes.get_changes_by(someuser)

or::

    Change.objects.get_changes_by_user(someuser)


You can also do things like this::

    Change.objects.all().by_user(someuser)
    changes.get_changes_for(someobj).anonymous()


Included is a 'Mixin' for your models that you expect to be recording changes
on a lot that will give you the reverse relation ``changes``::

    from changes.models import ChangesMixin
    # ...
    class SomeModel(ChangesMixin, models.Model)

This mixin will give you some helpful methods::

    somemodelinstance.add_change(why='Time for change')
    somemodelinstance.get_changes()

You can also add a change when saving::

    somemodelinstance.save(changed=True, who=someuser, why='Changing')

The default behaviour is to not save a change::

    somemodelinstance.save()

The mixin also omits a signal, ``change_added`` when a change is added for the
object.


See the source code for more.


Need Help?
==========

Email: rvause@gmail.com

Bitbucket: https://bitbucket.org/wearefarm/django-changes
