from django.core import serializers
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from .models import PointOfInterest

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