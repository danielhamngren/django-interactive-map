from django.urls import path

from . import views

app_name = 'tourism'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('get/ajax/poi', views.detail, name='poi_detail'),
    path('get/ajax/lazy', views.visible_poi, name='poi_load'),
    path('communes', views.CommuneView.as_view(), name='commune')
]
