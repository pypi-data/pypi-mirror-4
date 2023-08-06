from django.db import models
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from .signals import change_added


get_ct_for_model = ContentType.objects.get_for_model


class ChangeQuerySet(QuerySet):
    def for_object(self, obj, **kw):
        """
        Get changes for an obj
        """
        return self.filter(ct=get_ct_for_model(obj), obj_id=obj.id, **kw)

    def by_user(self, who, **kw):
        """
        Get changes by a given who
        """
        return self.filter(who=who, **kw)

    def anonymous(self, **kw):
        """
        Get changes with no who set
        """
        return self.filter(who__isnull=True, **kw)


class ChangeManager(models.Manager):
    def get_query_set(self):
        return ChangeQuerySet(self.model, using=self._db)

    def add_change_for_object(self, obj, **kw):
        """
        Create a new change for obj
        """
        when = kw.pop('when', timezone.now())
        return self.model.objects.create(
            c_obj=obj,
            when=when,
            **kw
        )

    def get_changes_for_object(self, obj, **kw):
        """
        Get changes for an obj
        """
        return self.get_query_set().for_object(obj, **kw)

    def get_changes_by_user(self, who, **kw):
        """
        Get changes by a given user
        """
        return self.get_query_set().by_user(who, **kw)

    def get_anonymous_changes(self, **kw):
        """
        Get changes that do not have the who set
        """
        return self.get_query_set().anonymous(**kw)


class Change(models.Model):
    """
    To store change details for something that has been modified

    Basically this model just stores a generic relation to an object which has
    been changed with this additional information
    """
    ct = models.ForeignKey(ContentType)
    obj_id = models.PositiveIntegerField()
    c_obj = generic.GenericForeignKey('ct', 'obj_id')

    when = models.DateTimeField()
    who = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    why = models.TextField(blank=True, null=True)

    objects = ChangeManager()

    class Meta:
        app_label = 'changes'
        ordering = ['-when']

    def __unicode__(self):
        return _('Change on %s (%s)') % (self.c_obj, self.ct)


class ChangesMixin(models.Model):
    """
    Mixin to provide the generic reverse relation on models that will commonly
    use changes
    """
    changes = generic.GenericRelation(Change, content_type_field='ct',
                                      object_id_field='obj_id')

    class Meta:
        abstract = True

    def save(self, changed=False, **kw):
        """
        Add a change for the model upon saving if changed is set to True
        """
        #  TODO: Act on why or who, not require "changed" unless no who or why
        if self.pk and changed:
            who = kw.pop('who', None)
            why = kw.pop('why', None)
            self.add_change(who=who, why=why)
        super(ChangesMixin, self).save(**kw)

    def add_change(self, **kw):
        """
        Add a Change
        """
        change = Change.objects.add_change_for_object(self, **kw)
        change_added.send(sender=self, change=change)
        return change

    def get_changes(self, **kw):
        """
        Get all changes for the object with filters
        """
        return Change.objects.get_changes_for_object(self, **kw)
