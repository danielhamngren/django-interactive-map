from django import forms
from django.contrib import messages
from django.contrib.gis import admin
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import Point
from django.contrib.messages import constants as messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import ngettext

import decimal
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
    extra = 0

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
    ## List
    list_display = ('name_link', 'commune', 'owner', 'is_tour')
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

    actions = ['make_tour']

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
    
    search_fields = ['name']
    list_filter = ['category', 'commune']

    ## CREATE & UPDATE
    fields = [
        'name',
        'description',
        'category',
        'location',
        ('street_address', 'commune'),
        ('email', 'phone', 'website'),
        'owner'
    ]

    inlines = [MainRepresentationInline, OpeningSchemaInline]

# == Tour == 
class GpxImportForm(forms.Form):
    gpx_file = forms.FileField()
    update_data = forms.BooleanField(
        required=True,
        label="Mis à jour des données",
        help_text="Si cette case est cochée, les informations (description, distance, durée, dénivelé, ...) \
            seront mises à jour selon les données fournies par le fichier GPX.",
        initial=True
    )

def form_handle_gpx_file(fn):
    def wrapper(self, request, *args, **kwargs):
        if request.method == "POST":
            form = GpxImportForm(request.POST, request.FILES)
            if form.is_valid():
                gpx_file = request.FILES["gpx_file"]
                gpx_path = gpx_file.temporary_file_path()
                ds = DataSource(gpx_path)
                tracks_layer = ds["tracks"]
                if len(tracks_layer) != 1:
                    self.message_user(request, "Le fichier GPX contient trop de traces.", level=messages.ERROR)
                    self.message_user(request, "Fichier GPX contenant trop de 'tracks'.", level=messages.DEBUG)
                    return redirect("..")
                trk = tracks_layer[0]

                update_data = form.cleaned_data['update_data']
                data = {"update_data": update_data, "trk": trk, "gpx_path": gpx_path}
                return fn(self, request, data, *args, **kwargs)

        # Render the template to upload a GPX file
        form = GpxImportForm()
        payload = {"form": form}
        return render(request, "admin/tourism/tour/gpx_upload.html", payload)
    return wrapper

def update_tour_data_from_gpx(tour, gpx_path, update_name=False):
    gpx = gpxpy.parse(open(gpx_path, 'r'))
    # Name
    if update_name and (name := gpx.name):
        tour.name = name.strip()
    # Description
    if desc := gpx.description:
        tour.description = desc.strip()
    # Distance
    tour.distance = tour.compute_length()
    # Time
    if duration := gpx.get_duration(): # in seconds
        tour.time = duration // 60
    # Elevation extremes
    elevation_ext = gpx.get_elevation_extremes()
    if ele_min := elevation_ext.minimum:
        tour.elevation_min = ele_min
    if ele_max := elevation_ext.maximum:
        tour.elevation_max = ele_max
    # Cumulation elevation
    gpx.simplify()
    uphill_downhill = gpx.get_uphill_downhill()
    if uphill := uphill_downhill.uphill:
        tour.uphill = uphill
    if downhill := uphill_downhill.downhill:
        tour.downhill = downhill


@admin.register(Tour)
class TourAdmin(GeoArgonne, nested_admin.NestedModelAdmin):
    exclude = ('dt_id', 'dt_categories', 'category')
    inlines = [MainRepresentationInline]

    def get_urls(self):
        urls = super(GeoArgonne, self).get_urls()
        my_urls = [
            path('<object_id>/import_gpx/', self.admin_site.admin_view(self.update_from_gpx), name='tourism_tour_update_from_gpx'),
            path('import_gpx/', self.admin_site.admin_view(self.add_from_gpx), name='tourism_tour_add_from_gpx')
        ]
        return my_urls + urls
    
    @form_handle_gpx_file
    def add_from_gpx(self, request, response):
        tour = Tour()
        tour.path = response["trk"].geom.geos
        tour.location = Point(tour.path[0][0])
        tour.is_closed = tour.get_is_closed()
        try:
            tour.commune = Commune.objects.get(geom__contains = tour.location)
        except Commune.DoesNotExist:
            self.message_user(request, "Aucune commune trouvée. Le parcours ne semble pas faire partie de l'Argonne.", level=messages.ERROR)
            return redirect("..")
        
        # Retrieve metadata info (name & desc)
        if response["update_data"]:
            update_tour_data_from_gpx(tour, response["gpx_path"], update_name=True)
        tour.save()

        self.message_user(request, "Votre fichier GPX a été importé avec succès.")
        return redirect("admin:tourism_tour_change", tour.pk)

    @form_handle_gpx_file
    def update_from_gpx(self, request, response, object_id):
        tour = get_object_or_404(Tour, pk=object_id)
        tour.path = response["trk"].geom.geos
        tour.location = Point(tour.path[0][0])
        tour.is_closed = tour.get_is_closed()

        if response["update_data"]:
            update_tour_data_from_gpx(tour, response["gpx_path"])
        tour.save()
        
        self.message_user(request, "Votre fichier GPX a été importé avec succès")
        return redirect("..")
