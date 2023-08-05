from django import forms
from django.forms.util import flatatt
from django.forms.widgets import RadioFieldRenderer
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

DAY_CHOICES = [('', '')] + zip(*[range(1, 32)] * 2)

MONTH_CHOICES = (
    ('', ''),
    (1, _('January')),
    (2, _('February')),
    (3, _('March')),
    (4, _('April')),
    (5, _('May')),
    (6, _('June')),
    (7, _('July')),
    (8, _('August')),
    (9, _('September')),
    (10, _('October')),
    (11, _('November')),
    (12, _('December')),
    )

HOUR_CHOICES = [('', '')] + zip(*[range(0, 24, 1)] * 2)

MINUTES = range(0, 60)
MINUTE_CHOICES = [('', '')] + zip(MINUTES, ['%02d' % m for m in MINUTES])


class AttrRadioFieldRenderer(RadioFieldRenderer):
    def render(self):
        """Outputs a <ul> for this set of radio fields."""
        attrs = flatatt(self.attrs)
        li = u'\n'.join([u'<li>%s</li>' % force_unicode(w) for w in self])
        return mark_safe(u'<ul%s>\n%s\n</ul>' % (attrs, li))


class BooleanSelect(forms.RadioSelect):
    renderer = AttrRadioFieldRenderer

    def render(self, name, value, attrs=None, choices=()):
        if attrs is None:
            attrs = {}
        attrs.update({'class': 'boolean'})
        value = int(value or 0)
        return super(BooleanSelect, self).render(name, value, attrs, choices)

    class Media:
        css = {
            'all': (
                'touchtechnology/public/admin/css/boolean.css',
                ),
            }


class SelectDateWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            forms.Select(choices=DAY_CHOICES, attrs=attrs),
            forms.Select(choices=MONTH_CHOICES, attrs=attrs),
            forms.TextInput(attrs=attrs),
            )
        super(SelectDateWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return (value.day, value.month, value.year)
        return (None, None, None)

    def format_output(self, rendered_widgets):
        return " ".join(rendered_widgets)


class SelectDateHiddenWidget(SelectDateWidget):
    def __init__(self, attrs=None):
        widgets = (
            forms.HiddenInput(attrs=attrs),
            forms.HiddenInput(attrs=attrs),
            forms.HiddenInput(attrs=attrs),
            )
        super(SelectDateWidget, self).__init__(widgets, attrs)


class SelectDateTimeWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            forms.Select(choices=DAY_CHOICES, attrs=attrs),
            forms.Select(choices=MONTH_CHOICES, attrs=attrs),
            forms.TextInput(attrs=attrs),
            forms.Select(choices=HOUR_CHOICES, attrs=attrs),
            forms.Select(choices=MINUTE_CHOICES, attrs=attrs),
            )
        super(SelectDateTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return (value.day, value.month, value.year,
                value.hour, value.minute)
        return (None, None, None, None, None)

    def format_output(self, rendered_widgets):
        date_part = " ".join(rendered_widgets[:-2])
        time_part = " ".join(rendered_widgets[-2:])
        output = """<span class="date_part">%s</span>
        <span class="time_part">%s</span>""" % (date_part, time_part)
        return output


class SelectDateTimeHiddenWidget(SelectDateTimeWidget):
    def __init__(self, attrs=None):
        widgets = (
            forms.HiddenInput(),
            forms.HiddenInput(),
            forms.HiddenInput(),
            forms.HiddenInput(),
            forms.HiddenInput(),
            )
        super(SelectDateTimeWidget, self).__init__(widgets, attrs)


class SelectTimeWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            forms.Select(choices=HOUR_CHOICES, attrs=attrs),
            forms.Select(choices=MINUTE_CHOICES, attrs=attrs),
            )
        super(SelectTimeWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return (value.hour, value.minute)
        return (None, None)

    def format_output(self, rendered_widgets):
        return " ".join(rendered_widgets)


class SelectTimeHiddenWidget(SelectTimeWidget):
    def __init__(self, attrs=None):
        widgets = (
            forms.HiddenInput(attrs=attrs),
            forms.HiddenInput(attrs=attrs),
            )
        super(SelectTimeWidget, self).__init__(widgets, attrs)
