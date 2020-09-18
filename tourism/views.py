from django.core import serializers
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from django.contrib.gis.geos import Polygon
from django.contrib.gis.db import models
from django.db.models import Value, When, Case, Exists, OuterRef


from .models import Category, Commune, OpeningHoursSchema, OpeningHours, PointOfInterest
from . import utils

import datetime
import json

class IndexView(ListView):
    template_name = 'tourism/index.html'
    context_object_name = 'category_list'

    def get_queryset(self):
        return Category.objects.order_by('order')

# def detail(request):
#     # return JsonResponse({"error": False}, status=200)
#     if request.is_ajax and request.method == "GET":
#         poi_id = request.GET.get("poi_id", None)
#         try:
#             poi = get_object_or_404(PointOfInterest, pk=poi_id)
#             poi_json = serializers.serialize('json', [poi, ])
#             return JsonResponse({"instance": poi_json}, status=200)
#         except PointOfInterest.DoesNotExist:
#             return JsonResponse({}, status=400)
#     return JsonResponse({}, status=400)

def ajax_get_view(view_function):
    def wrapper(request):
        if request.is_ajax and request.method == "GET":
            return view_function(request)
        else:
            return HttpResponseNotAllowed(('GET',))
    return wrapper

@ajax_get_view
def detail(request):
    poi_id = request.GET.get("poi_id", None)
    poi = get_object_or_404(PointOfInterest, pk=poi_id)

    if date_start_str := request.GET.get("date-from", None):
        date_start = datetime.datetime.strptime(date_start_str, '%Y-%m-%d').date()
        date_end = datetime.datetime.strptime(
            request.GET.get("date-to", "9999-12-31"), '%Y-%m-%d'
        ).date()
        opening_schema = OpeningHoursSchema.objects.filter(
            poi=poi,
            valid_from__lte=date_end,
            valid_through__gte=date_start,
            # openinghoursschema__openinghours__weekday__in = utils.get_isoweekdays_btw_dates(date_start, date_end),
        ).first()
        content = {
            'poi': poi,
            'requested_opening_schema': opening_schema
        }

    else: # get current opening_schema
        opening_schema = OpeningHoursSchema.objects.filter(
            poi=poi,
            valid_from__lte=datetime.date.today(),
            valid_through__gte=datetime.date.today()).first()
        content = {
            'poi': poi,
            'current_opening_schema': opening_schema
        }
    return render(request, 'tourism/index/_detail.html', content)

@ajax_get_view
def visible_poi(request):
    # Retrieve data
    categories = json.loads(request.GET.get("categories", None))
    name = json.loads(request.GET.get("name", None))

    # Retrieve dates
    date_start = datetime.datetime.strptime(
        request.GET.get("date-from", "2000-1-1"),
        '%Y-%m-%d'
    ).date()
    date_end = datetime.datetime.strptime(
        request.GET.get("date-to", "9999-12-31"),
        '%Y-%m-%d'
    ).date()

    if date_end < date_start:
        return render(
            request,
            'tourism/index/_poi_loader.html',
            {"error": f"La date de fin doit être supérieure à {date_start}."}
        )
    # Retrieve bounds
    # bounds = request.GET.get("bounds", None)
    # bounds_old = request.GET.get("boundsOld", None)  # not set if no move
    # geom_new = utils.to_geom(bounds)  # current zone (after zoom/drag)
    # geom_old = utils.to_geom(bounds_old)  # previous zone (bedore zoom/drag)
    # geom = geom_new - geom_old # new POis are inside this geometry

    # Query
    valid_openingschemas = OpeningHoursSchema.objects.filter(
        poi=OuterRef('pk'),
        valid_from__lte=date_end,
        valid_through__gte=date_start,
        openinghours__weekday__in=utils.get_isoweekdays_btw_dates(date_start, date_end),
    )
    poi_list = PointOfInterest.objects.filter(
        # location__within=geom_new,
        category__tag__in=categories,
    ).annotate(open=Exists(valid_openingschemas))

    if name:
        poi_by_commune_name = poi_list.filter(commune__name__icontains = name)
        poi_by_name = poi_list.filter(name__icontains = name)
        poi_list = poi_by_commune_name.union(poi_by_name)

    content = {
        'poi_list': poi_list.order_by('-open'),
    }
    return render(request, 'tourism/index/_poi_loader.html', content)

@ajax_get_view
def best_poi(request):
    POI_BY_PAGE = 10
    ids = json.loads(request.GET.get("ids", "[]"))
    page = int(request.GET.get("page", 0))
    best_results = PointOfInterest.objects.filter(pk__in = ids).order_by('name')[page*POI_BY_PAGE : (page+1)*POI_BY_PAGE]
    content = {
        'poi_list': best_results,
        # 'debug': best_results.count()
    }
    return render(request, 'tourism/index/_best_results.html', content)

# == DEBUG COMMUNE ==
class CommuneView(ListView):
    template_name = 'tourism/commune.html'
    context_object_name = 'commune_list'

    def get_queryset(self):
        return Commune.objects.all()