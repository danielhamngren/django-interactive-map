# Generated by Django 3.0.9 on 2020-10-01 17:04

from django.db import migrations, models
import django.db.models.deletion
import tourism.models

def transfer_data_from_poi_to_place(apps, schema_editor):
    PointOfInterest = apps.get_model('tourism', 'PointOfInterest')
    Place = apps.get_model('tourism', 'Place')
    for poi in PointOfInterest.objects.all():
        place = Place()
        place.category = poi.category
        place.subcategory = poi.subcategory
        place.is_always_open = poi.is_always_open
        place.name = poi.name
        place.save()
        poi.place_ptr = place.pk
        poi.save()


class Migration(migrations.Migration):

    dependencies = [
        ('tourism', '0024_transition_place_ptr'),
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='nom')),
                ('is_always_open', models.BooleanField(default=False, verbose_name='est en permanence ouvert')),
                ('category', models.ForeignKey(default=tourism.models.get_default_category, on_delete=django.db.models.deletion.PROTECT, to='tourism.Category')),
                ('subcategory', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tourism.SubCategory')),
            ],
        ),
        migrations.RunPython(transfer_data_from_poi_to_place),

        migrations.RemoveField(
            model_name='pointofinterest',
            name='id',
        ),
        migrations.AlterField(
            model_name='pointofinterest',
            name='place_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='tourism.Place'),
        ),
        migrations.RemoveField(
            model_name='pointofinterest',
            name='category',
        ),
        migrations.RemoveField(
            model_name='pointofinterest',
            name='is_always_open',
        ),
        migrations.RemoveField(
            model_name='pointofinterest',
            name='name',
        ),
        migrations.RemoveField(
            model_name='pointofinterest',
            name='subcategory',
        ),
    ]
