import json
import urllib2
import datetime
from decimal import Decimal
from django.core.management.base import NoArgsCommand
from django.conf import settings
from currency_rates.models import Currency, ExchangeRate

CURRENT_RATES_URL = "http://openexchangerates.org/latest.json"


class Command(NoArgsCommand):
    help = "Get the current rates from %s" % CURRENT_RATES_URL

    def handle_noargs(self, **options):

        app_id = getattr(settings, "OPENEXCHANGERATES_APP_ID", None)
        if not app_id:
            raise Exception("No OPENEXCHANGERATES_APP_ID defined in settings")

        base_currency = 'EUR'

        url = CURRENT_RATES_URL + "?app_id=" + app_id
        f = urllib2.urlopen(url)
        data = json.loads(f.read())

        base_currency_rate = Decimal(str(data['rates'][base_currency]))

        conversion = lambda x: Decimal(str(x)) / base_currency_rate
        date = datetime.date.fromtimestamp(data['timestamp'])

        ExchangeRate.objects.filter(date=date).delete()

        for code, rate in data['rates'].iteritems():
            try:
                currency = Currency.objects.get(code=code)
            except Currency.DoesNotExist:
                continue
            ExchangeRate.objects.create(currency=currency,
                            date=date, rate=conversion(rate))
