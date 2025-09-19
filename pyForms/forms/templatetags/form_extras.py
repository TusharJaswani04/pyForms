# forms/templatetags/form_extras.py
from django import template

register = template.Library()

@register.filter
def range_filter(start, end):
    """Create a range from start to end (inclusive)"""
    try:
        start = int(start)
        end = int(end)
        return range(start, end + 1)
    except (ValueError, TypeError):
        return range(1, 6)  # Default 1-5 range

@register.filter
def add(value, arg):
    """Add the arg to the value."""
    try:
        return int(value) + int(arg)
    except (ValueError, TypeError):
        return value
