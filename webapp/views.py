# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404
from django.shortcuts import get_object_or_404, render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

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
            request.user.restaurant_set.add(restaurant)
            return HttpResponseRedirect(reverse('webapp:detail', args=(restaurant.id,)))
    else:
        form = RestaurantForm()
    
    return render(request, 'webapp/restaurant_form.html', {'form':form})

@login_required
@permission_required('webapp.change_restaurant')
def restaurant_update(request, restaurant_id):
    if not int(restaurant_id) in [restaurant.id for restaurant in request.user.restaurant_set.all()]:
        raise Http404('You dont have permission to edit this Restaurant.')
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
@permission_required('webapp.add_cuisine')
def cuisine_create(request):
    return handle_popup_form(request, CuisineForm, 'cuisines')

@login_required
@permission_required('webapp.add_type')
def type_create(request):
    return handle_popup_form(request, TypeForm, 'types')

def signup(request, user_type):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            grp_obj, created = Group.objects.get_or_create(name=user_type)
            if created and user_type == 'owner':
                # Sets owner permissions for restaurant model
                set_permissions(grp_obj, 'webapp', 'restaurant' )
                set_permissions(grp_obj, 'webapp', 'type' )
                set_permissions(grp_obj, 'webapp', 'cuisine' )
            new_user.groups.add(grp_obj)
            return HttpResponseRedirect(reverse('login'))
    else:
        form = SignUpForm()
    
    context = {'form':form}
    return render(request, 'webapp/registration/signup_form.html', context=context)

def user_create(request):
    return signup(request, 'customer')

def owner_create(request):
    return signup(request, 'owner')

def set_permissions(grp_obj, app_name, model_name):
    content_type = ContentType.objects.get(app_label=app_name, model=model_name)
    permissions = Permission.objects.filter(content_type=content_type)

    for perms in permissions:
        grp_obj.permissions.add(perms)

def user_profile(request):
    restaurant_list = request.user.restaurant_set.all()
    return render(request, 'webapp/user_profile.html', {'restaurant_list':restaurant_list})
