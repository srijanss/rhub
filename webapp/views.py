# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db.models import Q

from .models import Restaurant
from .forms import RestaurantForm

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

def restaurant_create(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST)
        if form.is_valid():
            restaurant = form.save()             
            return HttpResponseRedirect(reverse('webapp:detail', args=(restaurant.id,)))
    else:
        form = RestaurantForm()
    
    return render(request, 'webapp/restaurant_form.html', {'form':form})

def restaurant_update(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    if request.method == 'POST':
        form = RestaurantForm(request.POST, instance=restaurant)
        if request.POST.get('delete_btn'):
            restaurant.delete()
            return HttpResponseRedirect(reverse('webapp:index'))
        else:
            if form.is_valid():
                restaurant = form.save()             
                return HttpResponseRedirect(reverse('webapp:detail', args=(restaurant.id,)))
    else:
        form = RestaurantForm(instance=restaurant)
    
    return render(request, 'webapp/restaurant_form.html', {'form':form, 'restaurant_id': restaurant_id})
