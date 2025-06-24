# inventory/templatetags/form_tags.py
from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    """
    Cette fonction permet d'ajouter une classe CSS à un champ de formulaire.
    """
    return value.as_widget(attrs={'class': arg})
