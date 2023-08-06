from django.utils.translation import ugettext_lazy as _
from django import forms
from widgets import InputMoneyWidget
from pymonon import Money, CURRENCIES, Currency

__all__ = ('MoneyField',)


class MoneyField(forms.DecimalField):
    def __init__(self, currency_widget=None, *args, **kwargs):
        self.widget = InputMoneyWidget(currency_widget=currency_widget)
        super(MoneyField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not isinstance(value, tuple):
            raise Exception("Invalid money input, expected sum and currency.")

        amount = super(MoneyField, self).to_python(value[0])
        currency = value[1]
        if not currency:
            raise forms.ValidationError(_(u'Currency is missing'))
        currency = currency.upper()
        if not CURRENCIES.get(currency, False) or currency == Currency.get_default().code:
            raise forms.ValidationError(_(u"Unrecognized currency type '%s'." % currency))
        return Money(amount=amount, currency=currency)

    def validate(self, value):
        if not isinstance(value, Money):
            raise Exception("Invalid money input, expected Money object to validate.")

        super(MoneyField, self).validate(value.amount)
