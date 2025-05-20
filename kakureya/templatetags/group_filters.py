from django import template

register = template.Library()

@register.filter(name='in_group')
def in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.filter(name='add_class')
def add_class(field, css):
    return field.as_widget(attrs={"class": css})

@register.filter
def until(value, max_value):
    """
    Devuelve un rango desde value hasta max_value (exclusivo).
    Útil para iterar: {% for i in 0|until:5 %}
    """
    try:
        return range(int(value), int(max_value))
    except:
        return []