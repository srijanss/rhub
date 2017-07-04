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
    url(r'^user/profile/$', views.user_profile, name='profile'),
    url(r'^restaurant/search/(?P<search_text>[a-zA-Z]+)/$', views.search_listing, name='search_listing'),
    url(r'^restaurant/(?P<restaurant_id>[0-9]+)/booking/$', views.booking_create, name='booking_create'),
    url(r'^restaurant/booking/update/(?P<booking_id>[0-9]+)/$', views.booking_update, name='booking_update'),
    url(r'^restaurant/booking/delete/(?P<booking_id>[0-9]+)/$', views.booking_delete, name='booking_delete'),
]