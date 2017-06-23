# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.template.loader import render_to_string
from django.forms import ModelForm, SelectMultiple, ModelMultipleChoiceField

from .models import Restaurant, Type, Cuisine, Food

class MultipleSelectWithPop(SelectMultiple):
    def render(self, name, *args, **kwargs):
        html = super(MultipleSelectWithPop, self).render(name, *args, **kwargs)
        popupplus = render_to_string("webapp/popupplus.html", {'field': name})
        return html+popupplus

class RestaurantForm(ModelForm):
    types = ModelMultipleChoiceField(Type.objects, widget=MultipleSelectWithPop) 
    cuisines = ModelMultipleChoiceField(Cuisine.objects, widget=MultipleSelectWithPop) 

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

