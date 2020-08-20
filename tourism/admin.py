from django import forms
from django.contrib.gis import admin
from django.contrib.gis.gdal import DataSource
from django.contrib.messages import constants as messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from django.urls import path

import nested_admin
from .models import Category, Commune, MainRepresentation, OpeningHours, OpeningHoursSchema, PointOfInterest, Tour

class GeoArgonne(admin.OSMGeoAdmin):
    default_zoom = 10
    default_lon = 554517 # 49.129889
    default_lat = 6297230 #4.981058

class OpeningHoursInline(nested_admin.NestedTabularInline):
    model = OpeningHours

class OpeningSchemaInline(nested_admin.NestedTabularInline):
    model = OpeningHoursSchema
    inlines = [OpeningHoursInline]
    extra = 1

class MainRepresentationInline(nested_admin.NestedTabularInline):
    model = MainRepresentation

@admin.register(Category)
class CategoryAdmin(GeoArgonne):
    # fields = ['name', 'tag']
    list_display = ('name', 'order')
    ordering = ('order', )
    list_editable = ('order', )
    exclude = ('tag', 'order')

@admin.register(Commune)
class CommuneAdmin(GeoArgonne):
    fields = [
        'name',
        'insee',
        'postal_code',
        'in_argonne_pnr',
        'geom',
    ]

@admin.register(PointOfInterest)
class PointOfInterestAdmin(GeoArgonne, nested_admin.NestedModelAdmin):
    list_display = ('name', 'commune')
    list_filter = ['commune']
    search_fields = ['name']

    fields = [
        'name',
        'description',
        'category',
        'location',
        ('street_address', 'commune'),
        ('email', 'phone', 'website')]

    inlines = [MainRepresentationInline, OpeningSchemaInline]


class GpxImportForm(forms.Form):
    gpx_file = forms.FileField()

def handle_uploaded_file(f):
    with open('test.txt', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

@admin.register(Tour)
class TourAdmin(GeoArgonne, nested_admin.NestedModelAdmin):

    inlines = [MainRepresentationInline]

    def get_urls(self):
        urls = super(GeoArgonne, self).get_urls()
        my_urls = [
            path('<object_id>/import_gpx/', self.admin_site.admin_view(self.import_gpx), name='tourism_tour_mylink'),
        ]
        return my_urls + urls
    
    def import_gpx(self, request, object_id):
        # GPX file has been uploaded
        if request.method == "POST":
            gpx_file = request.FILES["gpx_file"]

            # update tour
            tour = Tour.objects.get(pk=object_id)
            # handle_uploaded_file(gpx_file)
            ds = DataSource(gpx_file.temporary_file_path())
            tracks_layer = ds["tracks"]
            if len(tracks_layer) != 1:
                self.message_user(request, "Le fichier GPX semble corrompu.", level=messages.ERROR)
                self.message_user(request, "Fichier GPX contenant trop de 'tracks'", level=messages.DEBUG)
                return redirect("..")
            
            layer = tracks_layer[0]
            tour.path = layer.geom.geos
            tour.save()
            
            self.message_user(request, "Votre fichier GPX a été importé avec succès")
                
            # return redirect("admin:tourism_tour_change_list")
            return redirect("..")
            # return HttpResponse("Hello!" + str(type(layer.geom)))

        # Render the template to upload a GPX file
        form = GpxImportForm()
        payload = {"form": form}
        return render(request, "admin/tourism/tour/gpx_upload.html", payload)
        # context = dict(self.admin_site.each_context(request))
        # return TemplateResponse(request, "admin/tourism/tour/sometemplate.html", context)
        # return HttpResponse("Error Hello!" + str(object_id))