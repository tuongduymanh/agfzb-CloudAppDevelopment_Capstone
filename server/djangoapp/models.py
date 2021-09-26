from django.db import models
from django.utils.timezone import now


# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
class CarMake(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(null=False, max_length=50)
    description = models.CharField(null=False, max_length=200)
    
    def __str__(self):
        return "Name: " + self.name + ", " \
            "Description: " + self.description


# <HINT> Create a Car Model model `class CarModel(models.Model):`:
class CarModel(models.Model):
    id = models.AutoField(primary_key=True)
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    name = models.CharField(null=False, max_length=80)
    dealer_id = models.IntegerField(null=False)
    year = models.DateField()

    SUV = 'suv'
    SEDAN = 'sedan'
    WAGON = 'wagon'
    VAN = 'hatchaback'
    PICKUP = 'van'

    TYPES = [
        (SUV, 'suv'),
        (SEDAN, 'sedan'),
        (WAGON, 'wagon'),
        (VAN, 'hatchaback'),
        (PICKUP, 'van'),
    ]

    type = models.CharField(null=False, max_length=20, choices=TYPES)

    def __str__(self):
        return "Name: " + self.name + " Make: " \
            + self.make.name + " Type: " \
            + self.type + " Year: " \
            + str(self.year) + " Dealer ID: " + str(self.dealer_id)

class CarDealer:

    def __init__(self, address, city, full_name, id, lat, long, short_name, st, zip):
        # Dealer address
        self.address = address
        # Dealer city
        self.city = city
        # Dealer Full Name
        self.full_name = full_name
        # Dealer id
        self.id = id
        # Location lat
        self.lat = lat
        # Location long
        self.long = long
        # Dealer short name
        self.short_name = short_name
        # Dealer state
        self.st = st
        # Dealer zip
        self.zip = zip
        self.idx = 0

    def __str__(self):
        return "Dealer name: " + self.full_name


# <HINT> Create a plain Python class `DealerReview` to hold review data 
class DealerReview:
    def __init__(self, name, dealership, review, purchase, purchase_date, car_make, car_model, car_year, sentiment):
        self.name = name
        self.dealership = dealership
        self.review = review
        self.purchase = purchase
        self.purchase_date = purchase_date
        self.car_make = car_make
        self.car_model = car_model
        self.car_year = car_year
        self.sentiment = sentiment

    def __str__(self):
        return "Review: " + self.review
