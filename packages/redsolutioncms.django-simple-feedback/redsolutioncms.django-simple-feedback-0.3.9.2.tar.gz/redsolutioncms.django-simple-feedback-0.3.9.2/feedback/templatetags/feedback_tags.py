# -*- coding: utf-8 -*-

from django import template
from django.template import loader, Context
from django.forms import BooleanField
from feedback.utils import get_feedback_form
from django.utils.translation import ugettext_lazy as _

register = template.Library()


@register.simple_tag
def show_feedback(key='default'):
    form = get_feedback_form(key)()
    t = loader.select_template([
        'feedback/%s/feedback.html' % key,
        'feedback/feedback.html',
    ])
    output = t.render(Context(locals()))
    return output


@register.filter
def get_choice_value(bound_field):
    '''Returns verbose name of choice value'''
    value = None

    if hasattr(bound_field.form.fields[bound_field.name], 'choices'):
        for choice in bound_field.form.fields[bound_field.name].choices:
            if bound_field.data:
                if choice[0] == int(bound_field.data):
                    value = choice[1]
                    break;
            else:
                value = _('None')
    if value is None:
        if type(bound_field.form.fields[bound_field.name]) is BooleanField:
            if bound_field.data is None:
                return _('None')
            elif bound_field.data:
                return _('Yes')
            else:
                return _('No')
        else:
            return bound_field.data
    else:
        return value
