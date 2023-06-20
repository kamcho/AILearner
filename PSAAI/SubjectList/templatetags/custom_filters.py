from django import template

register = template.Library()

@register.filter
def divide(value, arg):
    value = int(value)
    try:
        return round((value / arg) * 100)
    except (ValueError, ZeroDivisionError):
        return 0
