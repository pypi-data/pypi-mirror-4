"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from pymonon import Money, CURRENCIES

from .dummyapp.models import (MoneyDefaultCurrencyModel, MoneyDefaultCurrencyCodeModel, MoneyDefaultCurrencyObjectModel,
                              CurrencyDefaultModel, CurrencyCodeModel, CurrencyObjectModel,
                              ModelWithVanillaMoneyField, ModelRelatedToModelWithMoney)


class MoneyFieldTest(TestCase):
    def test_save(self):
        obj = MoneyDefaultCurrencyModel()
        obj.money = 100.03
        obj.save()
        expected = Money(100.03)

        result = MoneyDefaultCurrencyModel.objects.get()

        self.assertEqual(expected, result.money)

    def test_create_float(self):
        obj = MoneyDefaultCurrencyModel.objects.create(money=100.03)
        expected = Money(100.03)

        result = MoneyDefaultCurrencyModel.objects.get()

        self.assertEqual(expected, result.money)

    def test_create_money(self):
        obj = MoneyDefaultCurrencyModel.objects.create(money=Money(100.03))
        expected = Money(100.03)

        result = MoneyDefaultCurrencyModel.objects.get()

        self.assertEqual(expected, result.money)

    def test_create_str(self):
        obj = MoneyDefaultCurrencyModel.objects.create(money='100.03')
        expected = Money(100.03)

        result = MoneyDefaultCurrencyModel.objects.get()

        self.assertEqual(expected, result.money)

    def test_create_default_currency_code(self):
        obj = MoneyDefaultCurrencyCodeModel.objects.create(money='100.03')
        expected = Money(100.03, 'CLP')

        result = MoneyDefaultCurrencyCodeModel.objects.get()

        self.assertEqual(expected, result.money)

    def test_create_default_currency_object(self):
        obj = MoneyDefaultCurrencyObjectModel.objects.create(money='100.03')
        expected = Money(100.03, 'ARS')

        result = MoneyDefaultCurrencyObjectModel.objects.get()

        self.assertEqual(expected, result.money)

    def test_save_money_different_from_default(self):
        obj = MoneyDefaultCurrencyModel.objects.create(money=Money(1000, 'CLP'))
        expected = Money(1000, 'CLP')

        result = MoneyDefaultCurrencyModel.objects.get()

        self.assertEqual(expected, result.money)

    def testExactMatch(self):

        somemoney = Money("100.0")

        model = ModelWithVanillaMoneyField()
        model.money = somemoney

        model.save()

        retrieved = ModelWithVanillaMoneyField.objects.get(money=somemoney)

        self.assertEquals(model.pk, retrieved.pk)

    def testRangeSearch(self):

        minMoney = Money("3")

        model = ModelWithVanillaMoneyField(money=Money("100.0"))

        model.save()

        retrieved = ModelWithVanillaMoneyField.objects.get(money__gt=minMoney)
        self.assertEquals(model.pk, retrieved.pk)

        shouldBeEmpty = ModelWithVanillaMoneyField.objects.filter(money__lt=minMoney)
        self.assertEquals(shouldBeEmpty.count(), 0)

    def testCurrencySearch(self):

        otherMoney = Money("1000", "USD")
        correctMoney = Money("1000", "CLP")

        model = ModelWithVanillaMoneyField(money=Money("100.0", "CLP"))
        model.save()

        shouldBeEmpty = ModelWithVanillaMoneyField.objects.filter(money__lt=otherMoney)
        self.assertEquals(shouldBeEmpty.count(), 0)

        shouldBeOne = ModelWithVanillaMoneyField.objects.filter(money__lt=correctMoney)
        self.assertEquals(shouldBeOne.count(), 1)


class CurrencyFieldTest(TestCase):
    def test_create_default(self):
        obj = CurrencyDefaultModel.objects.create()
        expected = CURRENCIES['USD']

        result = CurrencyDefaultModel.objects.get()

        self.assertEqual(expected.code, result.currency)

    def test_create_default_code(self):
        obj = CurrencyCodeModel.objects.create()
        expected = CURRENCIES['CLP']

        result = CurrencyCodeModel.objects.get()

        self.assertEqual(expected.code, result.currency)

    def test_create_default_object(self):
        obj = CurrencyObjectModel.objects.create()
        expected = CURRENCIES['ARS']

        result = CurrencyObjectModel.objects.get()

        self.assertEqual(expected.code, result.currency)

    def test_save_currency_code(self):
        obj = CurrencyDefaultModel.objects.create(currency='CLP')
        expected = CURRENCIES['CLP']

        result = CurrencyDefaultModel.objects.get()

        self.assertEqual(expected.code, result.currency)

    def test_save_currency_object(self):
        obj = CurrencyDefaultModel.objects.create(currency=CURRENCIES['CLP'])
        expected = CURRENCIES['CLP']

        result = CurrencyDefaultModel.objects.get()

        self.assertEqual(expected.code, result.currency)


class RelatedModelsTestCase(TestCase):

    def testFindModelsRelatedToMoneyModels(self):

        moneyModel = ModelWithVanillaMoneyField(money=Money("100.0", "CLP"))
        moneyModel.save()

        relatedModel = ModelRelatedToModelWithMoney(moneyModel=moneyModel)
        relatedModel.save()

        ModelRelatedToModelWithMoney.objects.get(moneyModel__money=Money("100.0", "CLP"))
        ModelRelatedToModelWithMoney.objects.get(moneyModel__money__lt=Money("1000.0", "CLP"))
