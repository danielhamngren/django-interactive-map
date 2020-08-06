from django.contrib.gis.db import models

class PointOfInterest(models.Model):
    name = models.CharField("nom", max_length=100)
    location = models.PointField("localication")
    street_address = models.CharField("adresse", max_length=100)
    city = models.CharField("commune", max_length=50)
    
    datatourism_id = models.CharField(max_length=200)
    categories = models.TextField(max_length=300)
    email = models.EmailField(max_length=50)
    phone = models.CharField(max_length=20)
    website = models.URLField(max_length=200)
    description = models.TextField()


    class Meta:
        ordering = ('name',)
        verbose_name = "point d'interêt"
        verbose_name_plural = "points d'interêt"


    def __str__(self):
        return f"{self.name} ({self.city})"