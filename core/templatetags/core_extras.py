import pprint

from django import template

register = template.Library()


@register.filter
def pprint_value(value):
    """Форматированный вывод dict/list для шаблонов."""
    return pprint.pformat(value, indent=2, width=88, sort_dicts=False)
