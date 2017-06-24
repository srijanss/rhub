# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404
from django.shortcuts import get_object_or_404, render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group

from .models import Restaurant, Cuisine, Type
from .forms import RestaurantForm, CuisineForm, TypeForm, SignUpForm

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

@login_required
@permission_required('webapp.add_restaurant')
def restaurant_create(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST)
        if form.is_valid():
            restaurant = form.save()             
            return HttpResponseRedirect(reverse('webapp:detail', args=(restaurant.id,)))
    else:
        form = RestaurantForm()
    
    return render(request, 'webapp/restaurant_form.html', {'form':form})

@login_required
@permission_required('webapp.change_restaurant')
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

@login_required
def handle_popup_form(request, PopUpForm, field):
    if request.method == 'POST':
        form = PopUpForm(request.POST)
        if form.is_valid():
            new_object = form.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        form = PopUpForm()
    
    context = {'form':form, 'field':field}
    return render(request, 'webapp/popup_form.html', context=context)

@login_required
@permission_required('webapp:add_cuisine')
def cuisine_create(request):
    return handle_popup_form(request, CuisineForm, 'cuisines')

@login_required
@permission_required('webapp:add_type')
def type_create(request):
    return handle_popup_form(request, TypeForm, 'types')

def signup(request, group_id):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            new_user.groups.add(Group.objects.get(pk=group_id))
            return HttpResponseRedirect(reverse('login'))
    else:
        form = SignUpForm()
    
    context = {'form':form}
    return render(request, 'webapp/registration/signup_form.html', context=context)

def user_create(request):
    return signup(request, 3)

def owner_create(request):
    return signup(request, 2)