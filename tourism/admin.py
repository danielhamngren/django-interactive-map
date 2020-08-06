from django.contrib.gis import admin
from .models import PointOfInterest

class GeoArgonne(admin.OSMGeoAdmin):
    default_zoom = 10
    default_lon = 554517 # 49.129889
    default_lat = 6297230 #4.981058

@admin.register(PointOfInterest)
class PointOfInterestAdmin(GeoArgonne):
    list_display = ('name', 'city')
    list_filter = ['city']
    search_fields = ['name']

    fields = ['name', 'description', 'location', ('street_address', 'city'), ('email', 'phone', 'website')]
