from django.db import models

from ..forms.fields import (
    BooleanChoiceField,
    SelectDateField,
    SelectDateTimeField,
    SelectTimeField,
    )
from ..mixins.schema import SouthTripleMixin


class BooleanField(SouthTripleMixin, models.BooleanField):
    """
    Custom `BooleanField` which overrides the formfield to use the much
    nicer `BooleanChoiceField` which presents two radio buttons rather
    than a checkbox.
    """
    def __init__(self, *args, **kwargs):
        # Custom `__init__` because the built-in BooleanField is expecting
        # a checkbox input where "unticked" == False and "ticked" == True.
        if 'default' not in kwargs and not kwargs.get('null'):
            kwargs['default'] = False
        models.Field.__init__(self, *args, **kwargs)

    def formfield(self, form_class=BooleanChoiceField, **kwargs):
        return super(BooleanField, self).formfield(
            form_class=form_class, **kwargs)


class DateField(SouthTripleMixin, models.DateField):
    def formfield(self, form_class=SelectDateField, **kwargs):
        return super(DateField, self).formfield(
            form_class=form_class, **kwargs)


class DateTimeField(SouthTripleMixin, models.DateTimeField):
    def formfield(self, form_class=SelectDateTimeField, **kwargs):
        return super(DateTimeField, self).formfield(
            form_class=form_class, **kwargs)


class TimeField(SouthTripleMixin, models.TimeField):
    def formfield(self, form_class=SelectTimeField, **kwargs):
        return super(TimeField, self).formfield(
            form_class=form_class, **kwargs)
