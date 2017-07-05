# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

import copy

from django.contrib.auth.models import User, Group

from .models import Restaurant, Type, Cuisine, Food, Booking
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

class BookModelTests(TestCase):
    
	def test_booking_object_creation(self):
		""" Booking object created must return restaurant name
		and booked date and time
		"""
		user = User.objects.create_user(username='test')
		restaurant = create_restaurant('Test Restaurant')
		booking_date = timezone.now()
		booking = Booking.objects.create(user=user, restaurant=restaurant, booking_date=booking_date, number_of_people=2)
		self.assertIs(isinstance(booking, Booking), True)
		self.assertEqual(booking.__str__(), booking.restaurant.name + ", Time: " + booking_date.strftime('%Y-%m-%d %H:%M:%S'))

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
		""" If restaurant with given id is not found message 
		Restaurant doesnot exists should be shown to user
		"""
		response = self.client.get(reverse('webapp:detail', args=(1,)), follow=True)
		messages = response.context['messages']
		message = ""
		for m in messages:
			message = m.message
		self.assertEqual(message, "Restaurant doesnot exists..")

	def test_with_restaurant(self):
		""" If restaurant exists restaurant details must shown in detail page
		"""
		restaurant = create_restaurant("Test Restaurant")
		response = self.client.get(
			reverse('webapp:detail', args=(restaurant.id,)))
		self.assertEqual(
			response.context['restaurant'].name, 'Test Restaurant')


class SearchViewTests(TestCase):
    def test_search_view_with_get_request(self):
        """ GET request to search page should redirect to listing page 
        and show all the listings of restaurants
        """
        response = self.client.get(reverse('webapp:search'))
        self.assertRedirects(response, reverse('webapp:search_listing', args=("all",)))

    def test_search_view_with_post_request(self):
        """ POST request to search page should redirect to listing page 
        and show the lists of restaurant matching the search item
        """
        create_restaurant("Test Restaurant")
        search_text = "test"
        response = self.client.post(reverse('webapp:search'), {'search_field':search_text})
        self.assertRedirects(response, reverse('webapp:search_listing', args=(search_text,)))
    
    def test_search_view_with_empty_data_request(self):
        """ POST request to search page with empty string should redirect to listing page 
        and show the all lists of restaurant
        """
        create_restaurant("Test Restaurant")
        search_text = ""
        response = self.client.post(reverse('webapp:search'), {'search_field':search_text})
        self.assertRedirects(response, reverse('webapp:search_listing', args=("all",)))

class SearchViewListingTests(TestCase):

    def test_no_matching_content(self):
        """ If search content doesnot match the restaurant name or type
        or restaurant doesnot exists, appropriate message should be shown
        """
        search_text = "test"
        response = self.client.get(reverse('webapp:search_listing', args=(search_text,)))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['search_list'], [])

    def test_name_matching_with_search_text(self):
        """ If search content match with the restaurant name
        that restaurant should be shown in the list
        """
        create_restaurant("Test Restaurant")
        search_text = "test"
        response = self.client.get(reverse('webapp:search_listing', args=(search_text,)))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['search_list'], ['<Restaurant: Test Restaurant>'])

    def test_type_matching_with_search_text(self):
        """ If search content match with the restaurant type
        that restaurant should be shown in the list
        """
        restaurant = create_restaurant("Test Restaurant")
        restaurant.types.create(name="Diner")
        search_text = "diner"
        response = self.client.get(reverse('webapp:search_listing', args=(search_text,)))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['search_list'], ['<Restaurant: Test Restaurant>'])

    def test_name_and_type_matching_with_search_text(self):
        """ If search content matches the restaurant name and type
        only one result of the matching restaurant should be shown
        """
        restaurant = create_restaurant("Diner Restaurant")
        restaurant.types.create(name="Diner")
        search_text = "diner"
        response = self.client.get(reverse('webapp:search_listing', args=(search_text,)))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['search_list'], ['<Restaurant: Diner Restaurant>'])

    def test_search_list_pagination_with_given_pagenumber(self):
        """ If page number is given as parameter then search list should
        show that page with the corresponding content
        """
        r1 = create_restaurant("Diner Restaurant 1")
        r2 = create_restaurant("Diner Restaurant 2")
        r3 = create_restaurant("Diner Restaurant 3")
        r4 = create_restaurant("Diner Restaurant 4")
        restaurant_type = Type.objects.create(name="Diner")
        restaurant_type.restaurant_set.add(r1, r2, r3, r4)
        search_text = "diner"
        page = 2
        response = self.client.get(reverse('webapp:search_listing', args=(search_text,)) + "?page="+str(page))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['search_list'], ['<Restaurant: Diner Restaurant 3>','<Restaurant: Diner Restaurant 4>'])


    def test_search_list_pagination_with_noninteger_pagenumber(self):
        """ If non integer page number is given as parameter then search list should
        show the first page with the corresponding content
        """
        r1 = create_restaurant("Diner Restaurant 1")
        r2 = create_restaurant("Diner Restaurant 2")
        r3 = create_restaurant("Diner Restaurant 3")
        r4 = create_restaurant("Diner Restaurant 4")
        restaurant_type = Type.objects.create(name="Diner")
        restaurant_type.restaurant_set.add(r1, r2, r3, r4)
        search_text = "diner"
        page = "two"
        response = self.client.get(reverse('webapp:search_listing', args=(search_text,)) + "?page="+str(page))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['search_list'], ['<Restaurant: Diner Restaurant 1>','<Restaurant: Diner Restaurant 2>'])

    def test_search_list_pagination_with_nonexisting_pagenumber(self):
        """ If non existing page number is given as parameter then search list should
        show the last page with the corresponding content
        """
        r1 = create_restaurant("Diner Restaurant 1")
        r2 = create_restaurant("Diner Restaurant 2")
        r3 = create_restaurant("Diner Restaurant 3")
        r4 = create_restaurant("Diner Restaurant 4")
        restaurant_type = Type.objects.create(name="Diner")
        restaurant_type.restaurant_set.add(r1, r2, r3, r4)
        search_text = "diner"
        page = 5
        response = self.client.get(reverse('webapp:search_listing', args=(search_text,)) + "?page="+str(page))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['search_list'], ['<Restaurant: Diner Restaurant 3>','<Restaurant: Diner Restaurant 4>'])


class RestaurantCreateViewTests(TestCase):

	def test_view_loads(self):
		""" View should be loaded for GET request
		"""
		create_owner('Test User', 'test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		response = self.client.get(reverse('webapp:restaurant_create'))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'webapp/restaurant_form.html')

	def test_view_fails_blank(self):
		""" Validation error should be shown if posted with blank data
		"""
		create_owner('Test User', 'test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		response = self.client.post(reverse('webapp:restaurant_create'), {})
		self.assertFormError(response, 'form', 'name', 'This field is required.')

	def test_view_fails_invalid(self):
		""" Validation error should be shown if invalid data is posted
		"""
		create_owner('Test User', 'test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		self.credentials = CREDENTIIALS.copy()
		self.credentials['longitude'] = 'error'
		response = self.client.post(
		    reverse('webapp:restaurant_create'), self.credentials)
		self.assertFormError(response, 'form', 'longitude', 'Enter a number.')

	def test_view_valid_post(self):
		""" If there is no validation error then it should redirect to restaurant's detail page
		"""
		create_owner('Test User', 'test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		type1 = Type.objects.create(name="test")
		cuisine1 = Cuisine.objects.create(name="test")
		self.credentials = CREDENTIIALS.copy()
		self.credentials["types"] = [type1.id]
		self.credentials["cuisines"] = [cuisine1.id]
		response = self.client.post(
		    reverse('webapp:restaurant_create'), self.credentials)
		self.assertRedirects(response, reverse('webapp:detail', args=(1,)))


class RestaurantUpdateViewTests(TestCase):

	def test_no_restaurant(self):
		""" If restaurant with given id is not found it should show message
			Restaurant doesnot exists 
		"""
		create_owner('Test User', 'test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		response = self.client.post(reverse('webapp:restaurant_update', args=(1,)), follow=True)
		messages = response.context['messages']
		message = ""
		for m in messages:
			message = m.message
		self.assertEqual(message, "Restaurant doesnot exists..")

	def test_view_loads(self):
		""" View loaded with data related to restaurant should be loaded for GET request
		"""
		owner = create_owner('Test User', 'test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		restaurant = create_restaurant("Test Restaurant")
		restaurant.users.add(owner)
		response = self.client.get(
		    reverse('webapp:restaurant_update', args=(restaurant.id,)))
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'webapp/restaurant_form.html')

	def test_view_fails_invalid(self):
		""" Validation error in updating should be shown if invalid data is posted
		"""
		owner = create_owner('Test User', 'test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		restaurant = create_restaurant("Test Restaurant")
		restaurant.users.add(owner)
		self.credentials = CREDENTIIALS.copy()
		self.credentials['longitude'] = 'error'
		response = self.client.post(
		    reverse('webapp:restaurant_update', args=(restaurant.id,)), self.credentials)
		self.assertFormError(response, 'form', 'longitude', 'Enter a number.')

	def test_view_valid_post(self):
		""" If there is no validation error then it should redirect to restaurant's detail page
		"""
		owner = create_owner('Test User', 'test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		type1 = Type.objects.create(name="test")
		cuisine1 = Cuisine.objects.create(name="test")
		self.credentials = CREDENTIIALS.copy()
		self.credentials["types"] = [type1.id]
		self.credentials["cuisines"] = [cuisine1.id]
		restaurant = create_restaurant("Test Restaurant")
		restaurant.users.add(owner)
		response = self.client.post(
		    reverse('webapp:restaurant_update', args=(restaurant.id,)), self.credentials)
		self.assertRedirects(response, reverse('webapp:detail', args=(1,)))

	def test_view_delete_restaurant(self):
		""" If there is delete_btn in POST request submission the restaurant object
		should be deleted and page must be redirected to index page"
		"""
		owner = create_owner('Test User', 'test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		restaurant = create_restaurant("Test Restaurant")
		restaurant.users.add(owner)
		response = self.client.post(reverse('webapp:restaurant_update', args=(
		    restaurant.id,)), {'delete_btn': 'delete_btn'})
		self.assertRedirects(response, reverse('webapp:index'))


class CuisineCreateViewTests(TestCase):

	def test_cuisine_create_form_pop_up(self):
		""" When Add cuisine button is pressed popup should appear with
		add cuisine form
		"""
		create_owner('Test User', 'test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		response = self.client.get(reverse('webapp:cuisine_create'))
		self.assertTemplateUsed(response, 'webapp/popup_form.html')

	def test_cuisine_create_form_with_blank_data(self):
		""" Cuisine create form should notify the error when blank data is submitted
		"""
		create_owner('Test User', 'test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		response = self.client.post(reverse('webapp:cuisine_create'), {})
		self.assertFormError(response, 'form', 'name', 'This field is required.')

	def test_cuisine_create_form_with_valid_data(self):
		""" Cuisine create form should disappear and notify of cuisine creation
		"""
		create_owner('Test User', 'test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		response = self.client.post(reverse('webapp:cuisine_create'), {
		                            'name': 'TEST CUISINE'})
		self.assertEqual(response.status_code, 302)
		# TODO: self.assertContains(response, 'New Cuisine Created.')


class TypeCreateViewTests(TestCase):
    def test_type_create_form_pop_up(self):
		""" When Add cuisine button is pressed popup should appear with
		add cuisine form
		"""
		create_owner('Test User', 'test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		response = self.client.get(reverse('webapp:type_create'))
		self.assertTemplateUsed(response, 'webapp/popup_form.html')
    
    def test_type_create_form_with_blank_data(self):
        """ Cuisine create form should notify the error when blank data is submitted
        """
        create_owner('Test User','test@example.com', 'testpwd')
        self.client.login(username='Test User', password='testpwd')
        response = self.client.post(reverse('webapp:type_create'), {})
        self.assertFormError(response, 'form', 'name', 'This field is required.')
	
    def test_type_create_form_with_valid_data(self):
		""" Cuisine create form should disappear and notify of cuisine creation
		"""
		create_owner('Test User','test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		response = self.client.post(reverse('webapp:type_create'), {'name':'TEST TYPE'})
		self.assertEqual(response.status_code, 302)
		# TODO: self.assertContains(response, 'New Cuisine Created.')


class UserCreateViewTests(TestCase):
    def test_user_create_view_loads(self):
        """ GET request to user create view must load the signup form
        """
        response = self.client.get(reverse('register_user'))
        self.assertTemplateUsed(response, 'webapp/registration/signup_form.html')

    def test_owner_create_view_load(self):
        """ GET request to owner create view must load the signup form
        """
        response = self.client.get(reverse('register_owner'))
        self.assertTemplateUsed(response, 'webapp/registration/signup_form.html')

    def test_user_create_view_valid_data(self):
        """ POST with valid request must redirect to login page
        """
        response = self.client.post(reverse('register_user'), {'username':'test', 'email':'test@example.com', 'password1':'TampereFI', 'password2':'TampereFI'})
        self.assertRedirects(response, reverse('login'))

    def test_owner_create_view_valid_data(self):
        """ POST with valid request must redirect to login page
        """
        response = self.client.post(reverse('register_owner'), {'username':'test', 'email':'test@example.com', 'password1':'TampereFI', 'password2':'TampereFI'})
        self.assertRedirects(response, reverse('login'))


class UserProfileViewTests(TestCase):

	def test_user_profile_view_loads(self):
		""" Profile view must be of the logged in user
		"""
		owner = create_owner('Test User','test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		response = self.client.get(reverse('webapp:profile'))
		self.assertContains(response, 'Test User')

	def test_user_profile_view_with_booking_list(self):
		""" Profile view of user must load with the list of bookings they have made
		"""
		user = User.objects.create_user(username='Test User', password='testpwd')
		group = Group.objects.create(name='customer')
		user.groups.add(group)
		self.client.login(username='Test User', password='testpwd')
		restaurant = create_restaurant("Test Restaurant")
		booking_date = datetime.datetime.now()
		booking = Booking.objects.create(user=user, restaurant=restaurant, booking_date=booking_date, number_of_people=2)
		response = self.client.get(reverse('webapp:profile'))
		self.assertQuerysetEqual(response.context['context_list'], ['<Booking: Test Restaurant, Time: ' + booking_date.strftime('%Y-%m-%d %H:%M:%S') + '>'])

	def test_owner_profile_view_with_restaurant_list(self):
		""" Profile view of owner must load with the list of restaurant they own
		"""
		owner = create_owner('Test User','test@example.com', 'testpwd')
		self.client.login(username='Test User', password='testpwd')
		restaurant = create_restaurant("Test Restaurant")
		restaurant.users.add(owner)
		response = self.client.get(reverse('webapp:profile'))
		self.assertQuerysetEqual(response.context['context_list'], ['<Restaurant: Test Restaurant>'])
	

class BookingViewTests(TestCase):
    
	def test_booking_creation_view_load(self):
		""" Booking creation view should load with restaurant selected 
		whose book table button was clicked
		"""
		restaurant = create_restaurant('Test Restauarant')
		response = self.client.get(reverse('webapp:booking_create', args=(restaurant.id,)))
		self.assertTemplateUsed(response, 'webapp/booking_form.html')
		self.assertEqual(response.context['restaurant_id'], str(restaurant.id))

	def test_booking_creation_view_without_login(self):
		""" Try to create Booking  without login should should show appropriate
			message and same booking create form should be displayed 
		"""
		restaurant = create_restaurant('Test Restauarant')
		user = User.objects.create_user(username='Test User', password='testpwd')
		booking_date = datetime.datetime.now()
		booking_credentials = {'user':user, 'restaurant':restaurant, 'booking_date':booking_date, 'number_of_people':2}
		response = self.client.post(reverse('webapp:booking_create', args=(restaurant.id,)), booking_credentials, follow=True)
		messages = response.context['messages']
		message = ""
		for m in messages:
			message = m.message
		self.assertEqual(message, 'You must Login to make bookings!!')
		self.assertRedirects(response, reverse('webapp:booking_create', args=(restaurant.id,)))
	
	def test_booking_create_view_with_invalid_data(self):
		""" Booking update view with invalid data 
		"""
		restaurant = create_restaurant('Test Restauarant')
		user = User.objects.create_user(username='Test User', password='testpwd')
		self.client.login(username='Test User', password='testpwd')
		booking_date = datetime.datetime.now()
		booking_credentials = {'user':user.id, 'restaurant':restaurant.id, 'booking_date':booking_date, 'number_of_people':'two', 'next':reverse('webapp:profile')}
		response = self.client.post(reverse('webapp:booking_create', args=(restaurant.id,)), booking_credentials, follow=True)
		self.assertFormError(response, 'form', 'number_of_people', 'Enter a whole number.')

	def test_booking_creation_view_with_login(self):
		""" Booking creation by logged in user should be redirected to 
			next url given in the POST reqeust
		"""
		restaurant = create_restaurant('Test Restauarant')
		user = User.objects.create_user(username='Test User', password='testpwd')
		self.client.login(username='Test User', password='testpwd')
		booking_date = datetime.datetime.now()
		booking_credentials = {'user':user.id, 'restaurant':restaurant.id, 'booking_date':booking_date, 'number_of_people':2, 'next':reverse('webapp:index')}
		response = self.client.post(reverse('webapp:booking_create', args=(restaurant.id,)), booking_credentials, follow=True)
		self.assertRedirects(response, reverse('webapp:index'))

	def test_booking_update_view_with_no_booking_found(self):
		""" If no booking found message must be shown to indicate that
		"""
		restaurant = create_restaurant('Test Restauarant')
		user = User.objects.create_user(username='Test User', password='testpwd')
		self.client.login(username='Test User', password='testpwd')
		response = self.client.get(reverse('webapp:booking_update', args=(1,)), follow=True)
		messages = response.context['messages']
		message = ""
		for m in messages:
			message = m.message
		self.assertEqual(message, 'Booking doesnot exists..')

	def test_booking_update_view_load(self):
		""" Booking update view should load with restaurant selected 
		whose book table button was clicked
		"""
		restaurant = create_restaurant('Test Restauarant')
		user = User.objects.create_user(username='Test User', password='testpwd')
		self.client.login(username='Test User', password='testpwd')
		booking_date = datetime.datetime.now()
		booking = Booking.objects.create(user=user, restaurant=restaurant, booking_date=booking_date, number_of_people=2)
		response = self.client.get(reverse('webapp:booking_update', args=(booking.id,)))
		self.assertTemplateUsed(response, 'webapp/booking_form.html')
		self.assertEqual(response.context['restaurant_id'], restaurant.id)
		self.assertEqual(response.context['booking_id'], str(booking.id))

	def test_booking_update_view_with_login(self):
		""" Booking update by logged in user should be redirected to 
			next url given in the POST reqeust
		"""
		restaurant = create_restaurant('Test Restauarant')
		user = User.objects.create_user(username='Test User', password='testpwd')
		self.client.login(username='Test User', password='testpwd')
		booking_date = datetime.datetime.now()
		booking = Booking.objects.create(user=user, restaurant=restaurant, booking_date=booking_date, number_of_people=2)
		booking_credentials = {'user':user.id, 'restaurant':restaurant.id, 'booking_date':booking_date, 'number_of_people':3, 'next':reverse('webapp:profile')}
		response = self.client.post(reverse('webapp:booking_update', args=(booking.id,)), booking_credentials, follow=True)
		self.assertRedirects(response, reverse('webapp:profile'))
	
	def test_booking_update_view_with_invalid_data(self):
		""" Booking update view with invalid data 
		"""
		restaurant = create_restaurant('Test Restauarant')
		user = User.objects.create_user(username='Test User', password='testpwd')
		self.client.login(username='Test User', password='testpwd')
		booking_date = datetime.datetime.now()
		booking = Booking.objects.create(user=user, restaurant=restaurant, booking_date=booking_date, number_of_people=2)
		booking_credentials = {'user':user.id, 'restaurant':restaurant.id, 'booking_date':booking_date, 'number_of_people':'two', 'next':reverse('webapp:profile')}
		response = self.client.post(reverse('webapp:booking_update', args=(booking.id,)), booking_credentials)
		self.assertFormError(response, 'form', 'number_of_people', 'Enter a whole number.')
	
	def test_booking_delete_view_when_booking_object_notfound(self):
		""" Booking delete view should show appropriate message 
			when trying to delete booking that doesnot exists
		"""
		restaurant = create_restaurant('Test Restauarant')
		user = User.objects.create_user(username='Test User', password='testpwd')
		self.client.login(username='Test User', password='testpwd')
		response = self.client.get(reverse('webapp:booking_delete', args=(1,)), follow=True)
		messages = response.context['messages']
		message = ""
		for m in messages:
			message = m.message
		self.assertEqual(message, 'Booking doesnot exists..')

	def test_booking_delete_view(self):
		""" Booking delete view should delete booking with message
		"""
		restaurant = create_restaurant('Test Restauarant')
		user = User.objects.create_user(username='Test User', password='testpwd')
		self.client.login(username='Test User', password='testpwd')
		booking_date = datetime.datetime.now()
		booking = Booking.objects.create(user=user, restaurant=restaurant, booking_date=booking_date, number_of_people=2)
		response = self.client.get(reverse('webapp:booking_delete', args=(booking.id,)), follow=True)
		messages = response.context['messages']
		message = ""
		for m in messages:
			message = m.message
		self.assertEqual(message, 'Booking removed.')
		
	
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
