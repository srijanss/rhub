# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import ModelForm

from .models import Restaurant, Type, Cuisine, Food

class RestaurantForm(ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'description', 'state', 'city', 'street', 'longitude', 'latitude', 'telephone', 'website', 'types', 'cuisines']

class TypeForm(ModelForm):
    class Meta:
        model = Type
        fields = ['name']

class CuisineForm(ModelForm):
    class Meta:
        model = Cuisine 
        fields = ['name']

class FoodForm(ModelForm):
    class Meta:
        model = Food 
        fields = ['name']