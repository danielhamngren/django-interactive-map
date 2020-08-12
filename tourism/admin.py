from django.contrib.gis import admin
import nested_admin
from .models import Category, Commune, MainRepresentation, OpeningHours, OpeningHoursSchema, PointOfInterest

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
    fields = ['name', 'tag']

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