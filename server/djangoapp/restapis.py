""" Djangoapp Rest APIs"""
import requests
import os
import json
from .models import *
from requests.auth import HTTPBasicAuth

API_URL_DEALERSHIP_GET = "https://service.eu.apiconnect.ibmcloud.com/gws/apigateway/api/5e2f7a8e6a9a514ec9998a8e70b88a0ce293fd848df7539953e8b384663236ac/api/api/dealerships/entries"
API_URL_REVIEW_GET = 'https://service.eu.apiconnect.ibmcloud.com/gws/apigateway/api/5e2f7a8e6a9a514ec9998a8e70b88a0ce293fd848df7539953e8b384663236ac/api/api/reviews/entries'
API_URL_REVIEW_POST = 'https://35ab1230.eu-gb.apigw.appdomain.cloud/api/api/reviews/save'
API_URL_DEALERSHIP_ADD = "https://35ab1230.eu-gb.apigw.appdomain.cloud/api/api/dealers/add"
API_URL_SENTIMENT = 'https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/88d0c1aa-ff76-44ea-ac93-f969b43db7d9'

# Create a `get_request` to make HTTP GET requests
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        response = requests.get(
            url, headers={'Content-Type': 'application/json'}, params=kwargs)
    except:
        print("Network exception occurred")
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
def post_request(url, json_payload, **kwargs):
    """ Post"""
    try:
        response = requests.post(url, json=json_payload, params=kwargs)
    except:
        print("Network exception occurred")
    json_data = json.loads(response.text)
    return json_data

# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealerships_from_cf():
    """ Get Dealerships"""
    results = []
    json_result = get_request(API_URL_DEALERSHIP_GET)
    if json_result:
        dealerships = json_result["entries"]
        for dealer in dealerships:
            car_dealer = CarDealer(id=dealer["id"],
                                   city=dealer["city"],
                                   state=dealer["state"],
                                   st=dealer["st"],
                                   address=dealer["address"],
                                   zip=dealer["zip"],
                                   lat=dealer["lat"],
                                   long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   full_name=dealer["full_name"])
            results.append(car_dealer)
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(dealerId):
    """ Get Reviews"""
    results = []
    json_result = get_request(API_URL_REVIEW_GET, dealerId=dealerId)
    if json_result:
        reviews = json_result["entries"]
        for review in reviews:
            sentiment = analyze_review_sentiments(review["review"])
            if(review["purchase"]):
                dealer_review = DealerReview(id=review["id"],
                                            dealership=review["dealership"],
                                            review=review["review"],
                                            purchase=review["purchase"],
                                            purchase_date=review['purchase_date'],
                                            car_make=review["car_make"],
                                            car_model=review["car_model"],
                                            car_year=review["car_year"],
                                            sentiment=sentiment)
                results.append(dealer_review)
            else:
                dealer_review = DealerReview(id=review["id"],
                                            dealership=review["dealership"],
                                            review=review["review"],
                                            purchase=review["purchase"],
                                            purchase_date="01/01/0000",
                                            car_make="None",
                                            car_model="None",
                                            car_year="None",
                                            sentiment=sentiment)
                results.append(dealer_review)
    return results

def add_dealer_review_to_db(review_post):
    """ Add Review """
    review = {
        "id": review_post['review_id'],
        "dealership": review_post['dealership'],
        "review": review_post['review'],
        "purchase": review_post.get('purchase', False),
        "purchase_date": review_post.get('purchase_date'),
        "car_make": review_post.get('car_make'),
        "car_model": review_post.get('car_model'),
        "car_year": review_post.get('car_year')
    }
    return post_request(API_URL_REVIEW_POST, review)


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
    url = "https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/88d0c1aa-ff76-44ea-ac93-f969b43db7d9"
    api_key = "ul4LUhas5N_IUWIGV1wfauUZ-8W1f9JfxbOgM_2ve79j"
    json_result = get_request(API_URL_SENTIMENT, text=text)
    if json_result:
        sentiment_result = json_result.get('label', 'neutral')
    return sentiment_result 