from django.contrib.gis import admin
import nested_admin
from .models import Category, OpeningHours, OpeningHoursSchema, PointOfInterest

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

@admin.register(PointOfInterest)
class PointOfInterestAdmin(GeoArgonne, nested_admin.NestedModelAdmin):
    list_display = ('name', 'city')
    list_filter = ['city']
    search_fields = ['name']

    fields = ['name', 'description', 'location', ('street_address', 'city'), ('email', 'phone', 'website')]
    inlines = [OpeningSchemaInline]
