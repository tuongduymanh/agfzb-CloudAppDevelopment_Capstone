""" Djangoapp Rest APIs"""
import requests
import os
import json
from .models import *
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, SentimentOptions

API_URL_DEALERSHIP_GET = "https://1602c818.us-south.apigw.appdomain.cloud/api/dealership"
API_URL_REVIEW_GET = 'https://1602c818.us-south.apigw.appdomain.cloud/api/review'
API_URL_REVIEW_POST = 'https://1602c818.us-south.apigw.appdomain.cloud/api/review'
API_URL_DEALERSHIP_ADD = "https://35ab1230.eu-gb.apigw.appdomain.cloud/api/api/dealers/add"
API_URL_SENTIMENT = 'https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/b39f2e76-9ea9-4787-b0de-8bb7f832c23b'
API_KEY_SENTIMENT = 'ytft4kgOtlpg31kSQnE7Yc_C1GzEYmiDKZa2qXS1h6if'


# Create a `get_request` to make HTTP GET requests
def get_request(url, apikey, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        if apikey:
            response = requests.get(url, params=kwargs, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', apikey))
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)
    except:
        print("Network exception occurred")
    json_data = json.loads(response.text)
    print(json_data)
    return json_data


# Create a `post_request` to make HTTP POST requests
def post_request(url, json_payload, **kwargs):
    """ Post"""
    try:
        response = requests.post(url, json=json_payload, params=kwargs)
    except:
        print("Network exception occurred")
    json_data = json.loads(response.text)
    print(response.text)
    return json_data


# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealerships_from_cf():
    """ Get Dealerships"""
    results = []
    json_result = get_request(API_URL_DEALERSHIP_GET, apikey="")
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
    json_result = get_request(API_URL_REVIEW_GET, apikey="", dealerId=dealerId)
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
                                            purchase_date="09/09/2021",
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
        "name": review_post['reviewer_name'],
        "dealership": review_post['dealership'],
        "review": review_post['review'],
        "purchase": review_post.get('purchase', False),
        "purchase_date": review_post.get('purchase_date'),
        "car_make": review_post.get('car_make'),
        "car_model": review_post.get('car_model'),
        "car_year": review_post.get('car_year')
    }
    print(review)
    return post_request(API_URL_REVIEW_POST, review)


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
    try:
        api_key = "mmj1AT11xuhlHJ7ZFeQcqoHT_MPwfwOn6Z-jxwGS0Chn"
        url = "https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/ddfed1cf-e08c-42d5-b19f-0337baaae49a"
        authenticator = IAMAuthenticator(api_key)
        natural_language_understanding = NaturalLanguageUnderstandingV1(
            version='2020-08-01',
            authenticator=authenticator
        )
        natural_language_understanding.set_service_url(url)
        response = natural_language_understanding.analyze(
            text=text,
            features=Features(sentiment=SentimentOptions())
        ).get_result()
        sentiment_label = response["sentiment"]["document"]["label"]
        sentimentresult = sentiment_label
    except:
        return ""
    return sentimentresult