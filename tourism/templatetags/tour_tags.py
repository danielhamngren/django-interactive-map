from django import template

register = template.Library()

@register.filter
def to_km(length_m):
    return str(round(length_m / 1000, 2)).replace('.', ',') + " km"

@register.filter
def to_hours(duration_min):
    if duration_min < 60:
        return f"{duration_min} min"
    else:
        hours = duration_min // 60
        mins = duration_min % 60
        return f"{hours} h {mins}"