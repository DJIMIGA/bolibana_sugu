from django import template

register = template.Library()


@register.filter(name='add_class')
def add_class(value, arg):
    if hasattr(value, 'as_widget'):
        return value.as_widget(attrs={'class': arg})
    elif hasattr(value, 'widget'):
        return value.widget.render(value.html_name, value.value(), attrs={'class': arg})
    return value
