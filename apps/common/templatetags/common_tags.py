import datetime
from django import template

register = template.Library()


@register.filter(name='check_list')
def check_list(value):
    """Return True if value is a list"""
    return isinstance(value, list)


@register.filter(name='create_date')
def create_date(value):
    return datetime.datetime(value.get('year'), value.get('month'), value.get('day'), value.get('hour'), value.get('minute'))
