from django import template
from tourism import utils
import datetime

register = template.Library()

@register.filter
def is_open(poi, date_start=None, date_end=None):
    "For the moment useless, since only 1 arg is allowed in templatetags"
    if not date_start:
        date_start = datetime.date(2020, 9, 3)
    if not date_end:
        date_end = datetime.date(2020, 9, 3)
    return utils.is_open(poi, date_start, date_end)