from django.contrib.gis.db import models

class Category(models.Model):
    name = models.CharField(max_length=150)
    tag = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=100)

    class Meta:
        verbose_name = "categorie"
        verbose_name_plural = "categories"

    def __str__(self):
        return f"[{self.tag}] {self.name}"

def get_default_category():
    cat = Category.objects.get_or_create(tag="default")[0]
    cat.icon = "default"
    if not cat.name:
        cat.name = "(pas de catégories)"
    cat.save()
    return cat.id



class PointOfInterest(models.Model):
    name = models.CharField("nom", max_length=100)
    location = models.PointField("localication")
    street_address = models.CharField("adresse", max_length=100)
    city = models.CharField("commune", max_length=50)
    
    dt_id = models.CharField(max_length=200)
    dt_categories = models.TextField(max_length=300)
    email = models.EmailField(max_length=50)
    phone = models.CharField(max_length=20)
    website = models.URLField(max_length=200)
    description = models.TextField()

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        default=get_default_category
    )

    class Meta:
        ordering = ('name',)
        verbose_name = "point d'interêt"
        verbose_name_plural = "points d'interêt"


    def __str__(self):
        return f"{self.name} ({self.city})"
