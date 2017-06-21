# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.test import TestCase

from .models import Restaurant, Type


class RestaurantModelTests(TestCase):

    def test_restaurant_object_creation(self):
        """
        Restaurant object created must return true for isinstance() and
        __str__() must be equal to restaurant's name
        """
        restaurant = create_restaurant("Test Restaurant")
        self.assertIs(isinstance(restaurant, Restaurant), True)
        self.assertEqual(restaurant.__str__(), restaurant.name)


class TypeModelTests(TestCase):

    def test_type_object_creation(self):
        """
        Type object created must return true for isinstance() and
        __str__() must be equal to restaurant's type 
        """
        restaurant_type = Type(name="Test Restaurant Type")
        self.assertIs(isinstance(restaurant_type, Type), True)
        self.assertEqual(restaurant_type.__str__(), restaurant_type.name)


class IndexViewTests(TestCase):

    def test_no_restaurants(self):
        """ If no Restaurant exists appropriate message should be displayed
        """
        response = self.client.get(reverse('webapp:index'))
        self.assertContains(response, "No restaurant added")
        self.assertQuerysetEqual(response.context['restaurant_list'], [])

    def test_one_restaurant(self):
        """ If one Restaurant exists it should be displayed in the index page
        """
        create_restaurant("Test Restaurant")
        response = self.client.get(reverse('webapp:index'))
        self.assertQuerysetEqual(response.context['restaurant_list'], [
                                 '<Restaurant: Test Restaurant>'])

    def test_two_restaurants(self):
        """ If two Restaurant exists both should be displayed in the index page
        """
        create_restaurant("Test Restaurant 1")
        create_restaurant("Test Restaurant 2")
        response = self.client.get(reverse('webapp:index'))
        self.assertQuerysetEqual(response.context['restaurant_list'],
                                 ['<Restaurant: Test Restaurant 2>',
                                     '<Restaurant: Test Restaurant 1>']
                                 )

class DetailViewTests(TestCase):
    
    def test_no_restaurant(self):
        """ If restaurant with given id is not found 404 error should be raise 
        """
        response = self.client.get(reverse('webapp:detail', args=(1,)))
        self.assertEqual(response.status_code, 404)
    
    def test_with_restaurant(self):
        """ If restaurant exists restaurant details must shown in detail page
        """
        restaurant = create_restaurant("Test Restaurant")
        response = self.client.get(reverse('webapp:detail', args=(restaurant.id,)))
        self.assertEqual(response.context['restaurant'].name, 'Test Restaurant')

class SearchViewTests(TestCase):
    
    def test_no_matching_content(self):
        """ If search content doesnot match the restaurant name or type 
        or restaurant doesnot exists, appropriate message should be shown
        """
        search_text = "test"
        response = self.client.post(reverse('webapp:search'), {'search_field':search_text})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['search_list'], [])

    def test_name_matching_with_search_text(self):
        """ If search content match with the restaurant name
        that restaurant should be shown in the list
        """
        create_restaurant("Test Restaurant")
        search_text = "test"
        response = self.client.post(reverse('webapp:search'), {'search_field':search_text})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['search_list'], ['<Restaurant: Test Restaurant>'])

    def test_type_matching_with_search_text(self):
        """ If search content match with the restaurant type
        that restaurant should be shown in the list
        """
        restaurant = create_restaurant("Test Restaurant")
        restaurant.types.create(name="Diner")
        search_text = "diner"
        response = self.client.post(reverse('webapp:search'), {'search_field':search_text})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['search_list'], ['<Restaurant: Test Restaurant>'])

    def test_name_and_type_matching_with_search_text(self):
        """ If search content matches the restaurant name and type 
        only one result of the matching restaurant should be shown
        """
        restaurant = create_restaurant("Diner Restaurant")
        restaurant.types.create(name="Diner")
        search_text = "diner"
        response = self.client.post(reverse('webapp:search'), {'search_field':search_text})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['search_list'], ['<Restaurant: Diner Restaurant>'])


# Helper functions
def create_restaurant(restaurant_name):
    return Restaurant.objects.create(name=restaurant_name,
                                     description="test restaurant",
                                     state="test",
                                     city="test",
                                     street="test",
                                     longitude=0.0,
                                     latitude=0.0,
                                     telephone="test",
                                     website="test.com")
