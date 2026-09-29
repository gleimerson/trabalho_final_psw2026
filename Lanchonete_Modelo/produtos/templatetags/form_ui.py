from django import template
from django.forms import CheckboxInput, RadioSelect, Select, SelectMultiple

register = template.Library()

@register.filter
def startswith(value, prefix):
    return bool(value and prefix and str(value).startswith(str(prefix)))

@register.filter
def bootstrap_field(bound_field):
    widget = bound_field.field.widget
    if isinstance(widget, (CheckboxInput, RadioSelect)):
        css = "form-check-input"
    elif isinstance(widget, (Select, SelectMultiple)):
        css = "form-select"
    else:
        css = "form-control"
    existing = widget.attrs.get("class", "")
    widget.attrs["class"] = (existing + " " + css).strip()
    return bound_field
