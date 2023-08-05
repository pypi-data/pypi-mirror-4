import json
import urllib2
from django.core.management.base import NoArgsCommand
from currency_rates.models import Currency

CURRENCIES_URL = "http://openexchangerates.org/currencies.json"


class Command(NoArgsCommand):
        help = "Load currencies from %s" % CURRENCIES_URL

        def handle_noargs(self, **options):

            f = urllib2.urlopen(CURRENCIES_URL)
            currencies = json.loads(f.read())

            for code, name in currencies.iteritems():
                try:
                    Currency.objects.get(code=code)
                except Currency.DoesNotExist:
                    Currency.objects.create(code=code, name=name)
