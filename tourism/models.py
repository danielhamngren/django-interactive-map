from django.contrib.gis.db import models
import datetime
# from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(max_length=150)
    tag = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=100)
    order = models.IntegerField("ordre")

    class Meta:
        verbose_name = "categorie"
        verbose_name_plural = "categories"

    def __str__(self):
        return f"{self.name}"

def get_default_category():
    cat = Category.objects.get_or_create(tag="default")[0]
    cat.icon = "default"
    if not cat.name:
        cat.name = "(pas de catégorie)"
    cat.save()
    return cat.id


# == Commune ==
class Commune(models.Model):
    name = models.CharField("nom", max_length=50)
    geom = models.MultiPolygonField("géométrie", null=True)
    insee = models.CharField(max_length=5, unique=True)
    postal_code = models.CharField(max_length=5)
    in_argonne_pnr = models.BooleanField("fait partie du PNR ?")

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f"{self.name}"


class PointOfInterest(models.Model):
    name = models.CharField("nom", max_length=100)
    location = models.PointField("localication")
    street_address = models.CharField("adresse", max_length=100, blank=True)
    commune = models.ForeignKey(
        Commune,
        on_delete=models.PROTECT,
    )
    
    dt_id = models.CharField(max_length=200)
    dt_categories = models.TextField(max_length=300)
    email = models.EmailField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(max_length=200, blank=True)
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
        return f"{self.name} ({self.commune.name})"


# == Management of opening hours ==
def get_valid_through_default():
        return datetime.date(datetime.date.today().year, 12, 31)

class OpeningHoursSchema(models.Model):
    """ Opening period """
    poi = models.ForeignKey(PointOfInterest, on_delete=models.CASCADE)
    valid_from = models.DateField("valable à partir du", default=datetime.date.today)
    valid_through= models.DateField("valable jusqu'au", blank=True, default=get_valid_through_default)


    class Meta:
        verbose_name = "période d'ouverture"
        verbose_name_plural = "périodes d'ouverture"
        ordering = ['valid_from', 'valid_through']

    def __str__(self):
        return f"{self.poi.name} ({self.valid_from} - {self.valid_through}"



class OpeningHours(models.Model):
    """ Typical week's opening hours during a certain opening period (schema) """
    WEEKDAYS = [
        (1, "Lundi"),
        (2, "Mardi"),
        (3, "Mercredi"),
        (4, "Jeudi"),
        (5, "Vendredi"),
        (6, "Samedi"),
        (7, "Dimanche"),
    ]

    schema = models.ForeignKey(OpeningHoursSchema, on_delete=models.CASCADE)
    weekday = models.PositiveSmallIntegerField("jour de la semaine", choices=WEEKDAYS)
    from_hour = models.TimeField("heure d'ouverture", null=True)
    to_hour = models.TimeField("heure de fermeture", null=True)

    class Meta:
        verbose_name = "horaires d'ouverture"
        verbose_name_plural = "horaires d'ouverture"
        ordering = ['weekday', 'from_hour']

    def __str__(self):
        return f"{self.schema.poi.name} {self.weekday} ({self.from_hour} - {self.to_hour})"

# == Media ==
class Media(models.Model):
    title = models.CharField("légende", max_length=150, null=True, blank=True)
    credits = models.CharField("crédits", max_length=100, null=True, blank=True)
    picture = models.ImageField()

    class Meta:
        abstract = True
        

def poi_directory_path(instance, filename):
    return f"poi_{instance.poi.id}/{filename}"

class MainRepresentation(Media):
    picture = models.ImageField(upload_to=poi_directory_path, verbose_name="image principale")
    poi = models.OneToOneField(
        PointOfInterest,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    class Meta:
        verbose_name = "image principale"
        verbose_name_plural = "images principales"