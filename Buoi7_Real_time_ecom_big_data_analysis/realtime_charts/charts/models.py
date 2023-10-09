from django.db import models

# Create your models here.


class SalesByCardType(models.Model):
    batch_no = models.IntegerField()
    card_type = models.CharField(max_length=50)
    total_sales = models.FloatField()


class SalesByCountry(models.Model):
    batch_no = models.IntegerField()
    country = models.CharField(max_length=50)
    total_sales = models.FloatField()