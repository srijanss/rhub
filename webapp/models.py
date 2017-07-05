# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import User

# Create your models here.
@python_2_unicode_compatible
class Type(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField('created date', auto_now_add=True)
    updated_at = models.DateTimeField('last modified', auto_now=True)

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class Cuisine(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField('created date', auto_now_add=True)
    updated_at = models.DateTimeField('last modified', auto_now=True)

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    telephone = models.CharField(max_length=100)
    website = models.URLField()
    types = models.ManyToManyField(Type)
    cuisines = models.ManyToManyField(Cuisine)
    created_at = models.DateTimeField('created date', auto_now_add=True)
    updated_at = models.DateTimeField('last modified', auto_now=True)
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class Food(models.Model):
    name = models.CharField(max_length=100)
    cuisine = models.ForeignKey(Cuisine, on_delete=models.CASCADE)
    created_at = models.DateTimeField('created date', auto_now_add=True)
    updated_at = models.DateTimeField('last modified', auto_now=True)

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class Booking(models.Model):
    name = models.CharField(max_length=250)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    booking_date = models.DateTimeField('Time to Book')
    number_of_people = models.IntegerField()
    special_message = models.TextField('Special Message', blank=True)
    created_at = models.DateTimeField('created date', auto_now_add=True)
    updated_at = models.DateTimeField('last modified', auto_now=True)

    def __str__(self):
        return self.restaurant.name + ", Time: " + self.booking_date.strftime('%Y-%m-%d %H:%M:%S')