# -*- coding: utf-8 -*-

from django import template
from django.template.defaultfilters import slugify

register = template.Library()

@register.filter
def in_list(value,arg):
    return value in arg


@register.filter
def in_dict(value,arg):
    for k,v in arg:
        if v == value:
            return 1
    return 0


@register.filter
def if_in(items, item):
    """
    This filter is a replacement for the if ... in ...
    expression in python.
    """
    try:
        if item in items:
            return True
    except:
        # this will raise an exception if list is not a list
        pass
    return False
    

@register.filter
def in_tags(item, items):
    """
    This filter will check if a item exists in a object list like:
    [<Tag: personal>, <Tag: twitt>]
    """
    try:
        values = [slugify(k) for k in items]
        if  item in values:
            return True
    except:
        # we should try to detect a specific error here!
        pass
    return False

