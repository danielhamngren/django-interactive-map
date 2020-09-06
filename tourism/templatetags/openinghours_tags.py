from django import template
from tourism import utils
import datetime

register = template.Library()

@register.filter
def is_open(poi, dates):
    "For the moment useless, since only 1 arg is allowed in templatetags"
    return dates
    if not date_start:
        date_start = datetime.date(2020, 9, 3)
    if not date_end:
        date_end = datetime.date(2020, 9, 3)
    return utils.is_open(poi, date_start, date_end)