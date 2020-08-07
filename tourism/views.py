from django.core import serializers
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from django.contrib.gis.geos import Polygon

from .models import PointOfInterest
import json

class IndexView(ListView):
    template_name = 'tourism/index.html'
    context_object_name = 'poi_list'  # default: question_list

    def get_queryset(self):
        return PointOfInterest.objects.all()

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
        return render(request, 'tourism/index/_detail.html', {'variable': poi})
    else:
        return HttpResponseNotAllowed(('GET',))

def visible_poi(request):
    if request.is_ajax and request.method == "GET":
        bounds = json.loads(request.GET.get("bounds", None))
        sw, ne = bounds["_southWest"], bounds["_northEast"]
        bbox = (sw["lng"], sw["lat"], ne["lng"], ne["lat"])
        geom = Polygon.from_bbox(bbox)
        poi_list = PointOfInterest.objects.filter(location__contained=geom)
        return render(request, 'tourism/index/_poi_loader.html', {'poi_list': poi_list})
    else:
        return HttpResponseNotAllowed(('GET',))