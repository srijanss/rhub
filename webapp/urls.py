from django.conf.urls import url

from . import views

app_name = 'webapp'
urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^restaurant/$', views.index, name="index"),
    url(r'^restaurant/(?P<restaurant_id>[0-9]+)/$', views.detail, name="detail"),
    url(r'^restaurant/search/$', views.search, name='search'),
    url(r'^restaurant/create/$', views.restaurant_create, name='restaurant_create'),
    url(r'^restaurant/update/(?P<restaurant_id>[0-9]+)/$', views.restaurant_update, name='restaurant_update'),
    url(r'^restaurant/types/create/$', views.type_create , name='type_create'),
    url(r'^restaurant/cuisines/create/$', views.cuisine_create , name='cuisine_create'),
]