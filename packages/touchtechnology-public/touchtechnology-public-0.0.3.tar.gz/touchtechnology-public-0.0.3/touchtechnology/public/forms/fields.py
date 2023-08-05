from datetime import date, datetime, time

from django import forms
from django.utils.translation import ugettext_lazy as _

from .widgets import (
    BooleanSelect,
    SelectDateWidget,
    SelectDateHiddenWidget,
    SelectDateTimeWidget,
    SelectDateTimeHiddenWidget,
    SelectTimeWidget,
    SelectTimeHiddenWidget,
    )

POSITIVE = _(u'Yes')
NEGATIVE = _(u'No')


class BooleanChoiceField(forms.TypedChoiceField):
    widget = BooleanSelect

    def __init__(self, positive=POSITIVE, negative=NEGATIVE, *args, **kwargs):
        choices = kwargs.pop('choices', ((1, positive), (0, negative)))
        super(BooleanChoiceField, self).__init__(choices=choices,
            coerce=lambda v: bool(int(v)), *args, **kwargs)


class SelectDateField(forms.MultiValueField):
    widget = SelectDateWidget
    hidden_widget = SelectDateHiddenWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.IntegerField(required=False),
            forms.IntegerField(required=False),
            forms.IntegerField(required=False),
            )
        super(SelectDateField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        return date(data_list[2], data_list[1], data_list[0])

    def clean(self, data):
        if not filter(None, data):
            return None
        try:
            day = int(data[0])
            month = int(data[1])
            year = int(data[2])
            d = date(year, month, day)
        except ValueError:
            raise forms.ValidationError('Please enter a valid date.')
        else:
            return d


class SelectDateTimeField(forms.MultiValueField):
    widget = SelectDateTimeWidget
    hidden_widget = SelectDateTimeHiddenWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.IntegerField(required=False),
            forms.IntegerField(required=False),
            forms.IntegerField(required=False),
            forms.IntegerField(required=False),
            forms.IntegerField(required=False),
            )
        super(SelectDateTimeField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        return date(data_list[2], data_list[1], data_list[0],
            data_list[3], data_list[4])

    def clean(self, data):
        if not filter(None, data):
            if self.required:
                raise forms.ValidationError('This field is required.')
            return None
        try:
            day = int(data[0])
            month = int(data[1])
            year = int(data[2])
            hour = int(data[3])
            minute = int(data[4])
            return datetime(year, month, day, hour, minute)
        except ValueError:
            raise forms.ValidationError('Please enter a valid date and time.')


class SelectTimeField(forms.MultiValueField):
    widget = SelectTimeWidget
    hidden_widget = SelectTimeHiddenWidget

    def __init__(self, *args, **kwargs):
        fields = (
            forms.IntegerField(required=False),
            forms.IntegerField(required=False),
            )
        super(SelectTimeField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        return time(data_list[0], data_list[1])

    def clean(self, data):
        if not filter(None, data):
            return None
        try:
            t = time(*map(int, data))
        except ValueError:
            raise forms.ValidationError('Please enter a valid time.')
        else:
            return t
