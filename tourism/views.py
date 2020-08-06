from django.shortcuts import render
from django.views.generic import ListView
from .models import PointOfInterest

class IndexView(ListView):
    template_name = 'tourism/index.html'
    context_object_name = 'poi_list'  # default: question_list

    def get_queryset(self):
        return PointOfInterest.objects.all()