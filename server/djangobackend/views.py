""" Djangoapp Views"""
import random
import os
import logging
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from server.djangoapp.restapis import *
from server.djangoapp.models import CarModel
# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create an `about` view to render a static about page
def about(request):
    """ About View"""
    context = {}
    if request.method == "GET":
        about_view = render(request, 'djangoapp/about.html', context)
    return about_view

    
# Create a `contact` view to return a static contact page
def contact(request):
    """ Contact View """
    context = {}
    if request.method == "GET":
        contact_view = render(request, 'djangoapp/contact.html', context)
    return contact_view

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            print(user)
            login(request, user)
            return render(request, 'djangoapp/index.html', context)
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    """ Logout Request """
    logout(request)
    logout_view = HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return logout_view

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    """ Registration Request """
    context = {}
    if request.method == 'GET':
        registration_view = render(request, 'djangoapp/registration.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
            messages.error(
                request, ("Username {} already exists!".format(username)))
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create_user(username=username,
                                            first_name=first_name,
                                            last_name=last_name,
                                            password=password)
            login(request, user)
            registration_view = render(request, 'djangoapp/index.html', context)
        else:
            registration_view = render(request, 'djangoapp/registration.html')
    return registration_view

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    """ Dealerships View """
    if request.method == "GET":
        dealerships = get_dealerships_from_cf()
        context = {"dealerships": dealerships}
        get_dealerships_view = render(request, 'djangoapp/index.html', context)
    return get_dealerships_view


def add_dealer_review(request, dealer_id, dealer_name):
    """ Add Review View """
    if request.method == "GET":
        cars = CarModel.objects.filter(dealer_id=dealer_id)
        context = {"cars": cars, "dealer_id": dealer_id,
                   "dealer_name": dealer_name}
        add_review_view = render(request, 'djangoapp/add_review.html', context)
    if request.method == "POST" and request.user.is_authenticated:
        form = request.POST
        review = {
            "review_id": random.randint(0, 100),
            "reviewer_name": form["fullname"],
            "dealership": dealer_id,
            "review": form["review"]
        }
        if form.get("purchase"):
            review["purchase"] = True
            review["purchase_date"] = form["purchasedate"]
            car = get_object_or_404(CarModel, pk=form["car"])
            review["car_make"] = car.carmake.name
            review["car_model"] = car.name
            review["car_year"] = car.year
        json_result = add_dealer_review_to_db(review)
        add_review_view = redirect(
            'djangoapp:dealer_reviews', dealer_id=dealer_id, dealer_name=dealer_name , cars = None)
    return add_review_view

def get_dealer_reviews(request, dealer_id, dealer_name):
    """ Dealerships Details """
    if request.method == "GET":
        dealer_reviews = get_dealer_reviews_from_cf(dealer_id)
        context = {
            "dealer_id": dealer_id,
            "dealer_name": dealer_name,
            "reviews": dealer_reviews
        }
        dealer_details_view = render(
            request, 'djangoapp/reviews.html', context)
    return dealer_details_view