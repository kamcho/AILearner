from django import template

register = template.Library()

@register.filter
def replace_string(value, arg):
    return value.replace(arg, "")
