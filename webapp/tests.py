# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.test import TestCase

import copy

from django.contrib.auth.models import User, Group

from .models import Restaurant, Type, Cuisine, Food
from .views import set_permissions

CREDENTIIALS = {
			'name': 'test',
			'description': 'test',
			'state': 'test',
			'city': 'test',
			'street': 'test',
			'longitude': 0.000111,
			'latitude': 0.000111,
			'telephone': '1234567890',
			'website': 'http://test.com'
		}

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
		restaurant_type = Type.objects.create(name="Test Restaurant Type")
		self.assertIs(isinstance(restaurant_type, Type), True)
		self.assertEqual(restaurant_type.__str__(), restaurant_type.name)


class CuisineModelTests(TestCase):

	def test_cuisine_object_creation(self):
		"""
		Cuisine object created must return true for isinstance() and
		__str__() must be equal to cuisine name 
		"""
		cuisine = Cuisine.objects.create(name="Test Cuisine")
		self.assertIs(isinstance(cuisine, Cuisine), True)
		self.assertEqual(cuisine.__str__(), cuisine.name)


class FoodModelTests(TestCase):

	def test_food_object_creation(self):
		"""
		Food object created must return true for isinstance() and
		__str__() must be equal to food name 
		"""
		cuisine = Cuisine.objects.create(name="Test Cuisine")
		food = Food.objects.create(name="Test Food", cuisine_id=cuisine.id)
		self.assertIs(isinstance(food, Food), True)
		self.assertEqual(food.__str__(), food.name)


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
		response = self.client.get(
			reverse('webapp:detail', args=(restaurant.id,)))
		self.assertEqual(
			response.context['restaurant'].name, 'Test Restaurant')


class SearchViewTests(TestCase):

	def test_no_matching_content(self):
		""" If search content doesnot match the restaurant name or type 
		or restaurant doesnot exists, appropriate message should be shown
		"""
		search_text = "test"
		response = self.client.post(reverse('webapp:search'), {
									'search_field': search_text})
		self.assertEqual(response.status_code, 200)
		self.assertQuerysetEqual(response.context['search_list'], [])

	def test_name_matching_with_search_text(self):
		""" If search content match with the restaurant name
		that restaurant should be shown in the list
		"""
		create_restaurant("Test Restaurant")
		search_text = "test"
		response = self.client.post(reverse('webapp:search'), {
									'search_field': search_text})
		self.assertEqual(response.status_code, 200)
		self.assertQuerysetEqual(response.context['search_list'], [
								 '<Restaurant: Test Restaurant>'])

	def test_type_matching_with_search_text(self):
		""" If search content match with the restaurant type
		that restaurant should be shown in the list
		"""
		restaurant = create_restaurant("Test Restaurant")
		restaurant.types.create(name="Diner")
		search_text = "diner"
		response = self.client.post(reverse('webapp:search'), {
									'search_field': search_text})
		self.assertEqual(response.status_code, 200)
		self.assertQuerysetEqual(response.context['search_list'], [
								 '<Restaurant: Test Restaurant>'])

	def test_name_and_type_matching_with_search_text(self):
		""" If search content matches the restaurant name and type 
		only one result of the matching restaurant should be shown
		"""
		restaurant = create_restaurant("Diner Restaurant")
		restaurant.types.create(name="Diner")
		search_text = "diner"
		response = self.client.post(reverse('webapp:search'), {
									'search_field': search_text})
		self.assertEqual(response.status_code, 200)
		self.assertQuerysetEqual(response.context['search_list'], [
								 '<Restaurant: Diner Restaurant>'])


class RestaurantCreateViewTests(TestCase):

	def test_view_loads(self):
		""" View should be loaded for GET request
		"""
		create_owner('Test User','test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		response = self.client.get(reverse('webapp:restaurant_create'))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'webapp/restaurant_form.html')

	def test_view_fails_blank(self):
		""" Validation error should be shown if posted with blank data
		"""
		create_owner('Test User','test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		response = self.client.post(reverse('webapp:restaurant_create'), {})
		self.assertFormError(response, 'form', 'name', 'This field is required.')

	def test_view_fails_invalid(self):
		""" Validation error should be shown if invalid data is posted
		"""
		create_owner('Test User','test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		self.credentials = CREDENTIIALS.copy()
		self.credentials['longitude'] = 'error'
		response = self.client.post(reverse('webapp:restaurant_create'), self.credentials)
		self.assertFormError(response, 'form', 'longitude', 'Enter a number.')

	def test_view_valid_post(self):
		""" If there is no validation error then it should redirect to restaurant's detail page
		"""
		create_owner('Test User','test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		type1 = Type.objects.create(name="test")
		cuisine1 = Cuisine.objects.create(name="test")
		self.credentials = CREDENTIIALS.copy()
		self.credentials["types"] = [type1.id]
		self.credentials["cuisines"] = [cuisine1.id]
		response = self.client.post(reverse('webapp:restaurant_create'), self.credentials)
		self.assertRedirects(response, reverse('webapp:detail', args=(1,)))

class RestaurantUpdateViewTests(TestCase):
	
	def test_no_restaurant(self):
		""" If restaurant with given id is not found 404 error should be raise 
		"""
		create_owner('Test User','test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		response = self.client.post(reverse('webapp:restaurant_update', args=(1,)))
		self.assertEqual(response.status_code, 404)
	
	def test_view_loads(self):
		""" View loaded with data related to restaurant should be loaded for GET request
		"""
		owner = create_owner('Test User','test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		restaurant = create_restaurant("Test Restaurant")
		restaurant.users.add(owner)
		response = self.client.get(reverse('webapp:restaurant_update', args=(restaurant.id,)))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'webapp/restaurant_form.html')

	def test_view_fails_invalid(self):
		""" Validation error in updating should be shown if invalid data is posted
		"""
		owner = create_owner('Test User','test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		restaurant = create_restaurant("Test Restaurant")
		restaurant.users.add(owner)
		self.credentials = CREDENTIIALS.copy() 
		self.credentials['longitude'] = 'error'
		response = self.client.post(reverse('webapp:restaurant_update', args=(restaurant.id,)), self.credentials)
		self.assertFormError(response, 'form', 'longitude', 'Enter a number.')

	def test_view_valid_post(self):
		""" If there is no validation error then it should redirect to restaurant's detail page
		"""
		owner = create_owner('Test User','test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		type1 = Type.objects.create(name="test")
		cuisine1 = Cuisine.objects.create(name="test")
		self.credentials = CREDENTIIALS.copy()
		self.credentials["types"] = [type1.id]
		self.credentials["cuisines"] = [cuisine1.id]
		restaurant = create_restaurant("Test Restaurant")
		restaurant.users.add(owner)
		response = self.client.post(reverse('webapp:restaurant_update', args=(restaurant.id,)), self.credentials)
		self.assertRedirects(response, reverse('webapp:detail', args=(1,)))

	def test_view_delete_restaurant(self):
		""" If there is delete_btn in POST request submission the restaurant object
		should be deleted and page must be redirected to index page"
		"""
		owner = create_owner('Test User','test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		restaurant = create_restaurant("Test Restaurant")
		restaurant.users.add(owner)
		response = self.client.post(reverse('webapp:restaurant_update', args=(restaurant.id,)), {'delete_btn':'delete_btn'})
		self.assertRedirects(response, reverse('webapp:index'))

class CuisineCreateViewTests(TestCase):
	
	def test_cuisine_create_form_pop_up(self):
		""" When Add cuisine button is pressed popup should appear with 
		add cuisine form 
		"""
		create_owner('Test User','test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		response = self.client.get(reverse('webapp:cuisine_create'))
		self.assertTemplateUsed(response, 'webapp/popup_form.html')

	def test_cuisine_create_form_with_blank_data(self):
		""" Cuisine create form should notify the error when blank data is submitted
		"""
		create_owner('Test User','test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		response = self.client.post(reverse('webapp:cuisine_create'), {})
		self.assertFormError(response, 'form', 'name', 'This field is required.')
	
	def test_cuisine_create_form_with_valid_data(self):
		""" Cuisine create form should disappear and notify of cuisine creation
		"""
		create_owner('Test User','test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		response = self.client.post(reverse('webapp:cuisine_create'), {'name':'TEST CUISINE'})
		self.assertEqual(response.status_code, 302)
		# TODO: self.assertContains(response, 'New Cuisine Created.')
	
class TypeCreateViewTests(TestCase):
	
	def test_type_create_form_pop_up(self):
		""" When Add cuisine button is pressed popup should appear with 
		add cuisine form 
		"""
		create_owner('Test User','test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		response = self.client.get(reverse('webapp:type_create'))
		self.assertTemplateUsed(response, 'webapp/popup_form.html')

	def test_cuisine_create_form_with_blank_data(self):
		""" Cuisine create form should notify the error when blank data is submitted
		"""
		create_owner('Test User','test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		response = self.client.post(reverse('webapp:type_create'), {})
		self.assertFormError(response, 'form', 'name', 'This field is required.')
	
	def test_cuisine_create_form_with_valid_data(self):
		""" Cuisine create form should disappear and notify of cuisine creation
		"""
		create_owner('Test User','test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		response = self.client.post(reverse('webapp:type_create'), {'name':'TEST TYPE'})
		self.assertEqual(response.status_code, 302)
		# TODO: self.assertContains(response, 'New Cuisine Created.')


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

def create_owner(username, email, password):
	user = User.objects.create_user(username=username, email=email, password=password)
	group = Group.objects.create(name='owner')
	set_permissions(group, 'webapp', 'restaurant')
	set_permissions(group, 'webapp', 'type')
	set_permissions(group, 'webapp', 'cuisine')
	user.groups.add(group)
	return user
