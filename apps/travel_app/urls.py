
from django.conf.urls import url, include
from . import views
urlpatterns = [
    url(r'^$', views.index),
    url(r'^register$', views.register),
    url(r'^login$', views.login),
    url(r'^logout$', views.logout),
    url(r'^travels$', views.travels),
    url(r'^travels/add$', views.travels_add),
    url(r'^travels/create$', views.travel_create),
    url(r'^travels/join/(?P<travel_id>\d+)$', views.travel_join),
    url(r'^travels/destination/(?P<travel_id>\d+)$', views.travels_view),
]
