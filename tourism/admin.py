from django import forms
from django.contrib import messages
from django.contrib.gis import admin
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import Point
from django.contrib.messages import constants as messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import ngettext

import nested_admin
import gpxpy
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
    list_display = ('name_link', 'commune', 'is_tour')
    list_display_links = None

    def name_link(self, poi):
        try:
            poi.tour
            url = reverse('admin:tourism_tour_change', args=[poi.pk])
        except Tour.DoesNotExist:
            url = reverse('admin:tourism_pointofinterest_change', args=[poi.pk])
        return format_html(f"<a href='{url}'><b>{poi.name}</b></a>")
    # name_link.allow_tags = True
    name_link.short_description = "nom"

    def is_tour(self, poi):
        try:
            poi.tour
            return True
        except Tour.DoesNotExist:
            return False
    is_tour.short_description = "Randonnée"
    is_tour.boolean = True

    def make_tour(self, request, queryset):
        nb_updated = 0
        for poi in queryset:
            try: # already a Tour
                poi.tour
                continue
            except Tour.DoesNotExist:
                nb_updated += 1
                t = Tour(name=poi.name, location=poi.location, commune=poi.commune)
                t.pointofinterest_ptr = poi
                t.save()
                poi.tour = t
                poi.save()
        self.message_user(request, ngettext(
            "%d point d'intérêt a été converti en randonnée.",
            "%d points d'intérêt ont été convertis en randonnées.",
            nb_updated,
        ) % nb_updated, messages.SUCCESS)
    make_tour.short_description = "Convertir en randonnée(s)."
    
    actions = ['make_tour']
    search_fields = ['name']
    list_filter = ['category', 'commune']

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
    exclude = ('dt_id', 'dt_categories', 'category')
    inlines = [MainRepresentationInline]

    def get_urls(self):
        urls = super(GeoArgonne, self).get_urls()
        my_urls = [
            path('<object_id>/import_gpx/', self.admin_site.admin_view(self.import_gpx), name='tourism_tour_update_from_gpx'),
            path('import_gpx/', self.admin_site.admin_view(self.add_from_gpx), name='tourism_tour_add_from_gpx')
        ]
        return my_urls + urls
    
    def add_from_gpx(self, request):
        if request.method == "POST":
            gpx_file = request.FILES["gpx_file"]

            tour = Tour()
            ds = DataSource(gpx_file.temporary_file_path())
            tracks_layer = ds["tracks"]
            if len(tracks_layer) != 1:
                self.message_user(request, "Le fichier GPX semble corrompu.", level=messages.ERROR)
                self.message_user(request, "Fichier GPX contenant trop de 'tracks'", level=messages.DEBUG)
                return redirect("..")
            layer = tracks_layer[0]
            tour.path = layer.geom.geos
            tour.location = Point(tour.path[0][0])
            try:
                tour.commune = Commune.objects.get(geom__contains = tour.location)
            except Commune.DoesNotExist:
                self.message_user(request, "La commune ne semble pas faire partie de l'Argonne.", level=messages.ERROR)
                return redirect("..")
            gpx = gpxpy.parse(open(gpx_file.temporary_file_path(), 'r'))
            if desc := gpx.description:
                tour.description = desc.strip()
            if name := gpx.name:
                tour.name = name.strip()
            tour.save()

            self.message_user(request, "Votre fichier GPX a été importé avec succès.")
        form = GpxImportForm()
        payload = {"form": form}
        return render(request, "admin/tourism/tour/gpx_upload.html", payload)
    
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
            tour.location = Point(tour.path[0][0])
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