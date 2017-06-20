from django.conf.urls import url

from . import views

app_name = 'webapp'
urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^restaurant/$', views.index, name="index"),
    url(r'^restaurant/(?P<restaurant_id>[0-9]+)/$', views.detail, name="detail"),
]