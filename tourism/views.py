from django.core import serializers
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from django.contrib.gis.geos import Polygon

from .models import Category, OpeningHoursSchema, OpeningHours, PointOfInterest
from . import utils

import datetime
import json

class IndexView(ListView):
    template_name = 'tourism/index.html'
    context_object_name = 'category_list'

    def get_queryset(self):
        return Category.objects.all().order_by('order')

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

def detail(request):
    if request.is_ajax and request.method == "GET":
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
    else:
        return HttpResponseNotAllowed(('GET',))

def visible_poi(request):
    if request.is_ajax and request.method == "GET":
        # Retrieve data
        bounds = json.loads(request.GET.get("bounds", None))
        categories = json.loads(request.GET.get("categories", None))
        date_start = datetime.datetime.strptime(
            request.GET.get("date-from", "2000-1-1"),
            '%Y-%m-%d'
        ).date()
        date_end = datetime.datetime.strptime(
            request.GET.get("date-to", "9999-12-31"),
            '%Y-%m-%d'
        ).date()

        if date_end < date_start:
            return render(request, 'tourism/index/_poi_loader.html', {"error": f"La date de fin doit être supérieure à {date_start}."})

        sw, ne = bounds["_southWest"], bounds["_northEast"]
        bbox = (sw["lng"], sw["lat"], ne["lng"], ne["lat"])
        geom = Polygon.from_bbox(bbox)
        poi_list = PointOfInterest.objects.filter(
            location__contained=geom,
            category__tag__in=categories,
            # openinghoursschema__valid_from__lte = date_end,
            # openinghoursschema__valid_through__gte = date_start,
            # openinghoursschema__openinghours__weekday__in = utils.get_isoweekdays_btw_dates(date_start, date_end),
        ).distinct()
                
        content = {'poi_list': poi_list}
        return render(request, 'tourism/index/_poi_loader.html', content)
    else:
        return HttpResponseNotAllowed(('GET',))