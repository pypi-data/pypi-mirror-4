from django.db import models

from ..models import ChangesMixin


class ChangesTestModel(ChangesMixin, models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'tests'
