from django.db import models

from pymonon import CURRENCIES

from monon.models.fields import MoneyField, CurrencyField


class MoneyDefaultCurrencyModel(models.Model):
    money = MoneyField()
    

class MoneyDefaultCurrencyCodeModel(models.Model):
    money = MoneyField(default_currency='CLP')


class MoneyDefaultCurrencyObjectModel(models.Model):
    money = MoneyField(default_currency=CURRENCIES['ARS'])


class CurrencyDefaultModel(models.Model):
    currency = CurrencyField()


class CurrencyCodeModel(models.Model):
    currency = CurrencyField(default='CLP')


class CurrencyObjectModel(models.Model):
    currency = CurrencyField(default=CURRENCIES['ARS'])


class ModelWithVanillaMoneyField(models.Model):    
    money = MoneyField(max_digits=10, decimal_places=2)
    
class ModelRelatedToModelWithMoney(models.Model):
    
    moneyModel = models.ForeignKey(ModelWithVanillaMoneyField)