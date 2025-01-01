from django import template
from datetime import datetime, timedelta

register = template.Library()


@register.filter
def add_days(value, days):
    """
    Add a specified number of days to a date.
    Usage: {{ value|add_days:days }}
    """
    if not value:
        return value
    try:
        # Convert string to datetime if needed
        if isinstance(value, str):
            value = datetime.strptime(value, '%Y-%m-%d')
        return value + timedelta(days=int(days))
    except (ValueError, TypeError):
        return value


# store/templatetags/store_filters.py
# You can add store-specific filters here if needed
from django import template

register = template.Library()


# Example store-specific filter
@register.filter
def currency(value):
    """
    Format a number as currency
    Usage: {{ value|currency }}
    """
    try:
        return f"${value:.2f}"
    except (ValueError, TypeError):
        return value