from django.contrib import admin
from .models import *

# CarModelInline class
class CarModelInline(admin.StackedInline):
    model = CarModel
    extra = 5

# CarModelAdmin class
class CarModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'carmake', 'year', 'type']
    list_filter = ['carmake']
    search_fields = ['name', 'carmake']

# CarMakeAdmin class with CarModelInline
class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]
    list_display = ('name', 'description')
    list_filter = ['name']
    search_fields = ['name']

# Register models here
admin.site.register(CarModel, CarModelAdmin) 
admin.site.register(CarMake, CarMakeAdmin)