# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db.models import Q

from .models import Restaurant

# Create your views here.
def index(request):
    restaurant_list = Restaurant.objects.order_by('-created_at') [:5]
    context = { 'restaurant_list': restaurant_list }
    return render(request, 'webapp/index.html', context)

def detail(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    return render(request, 'webapp/detail.html', {'restaurant':restaurant})

def search(request):
    search_text = request.POST['search_field']
    restaurant_list = Restaurant.objects.filter(Q(name__icontains=search_text) | Q(types__name__icontains=search_text)).distinct()
    return render(request, 'webapp/search_result.html', {'search_list':restaurant_list})