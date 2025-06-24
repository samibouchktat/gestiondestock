from django import template

register = template.Library()


# inventory/templatetags/custom_filters.py
register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Ajoute la classe CSS `css_class` au widget d'un BoundField.
    Si l'objet n'est pas un BoundField, on renvoie l'entrée sans modification.
    """
    # Vérifie qu'on a bien un BoundField
    try:
        widget = field.field.widget
    except Exception:
        return field
    # Récupère et met à jour les classes existantes
    existing = widget.attrs.get('class', '')
    combined = f"{existing} {css_class}".strip()
    widget.attrs['class'] = combined
    return field
