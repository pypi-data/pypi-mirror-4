import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _


def default_currency():
    try:
        return Currency.objects.get(is_default=True)
    except Currency.DoesNotExist:
        pass

    try:
        return Currency.objects.get(code='EUR')
    except Currency.DoesNotExist:
        pass

    return None


class Currency(models.Model):
    code = models.CharField(_('Code'), max_length=3, unique=True)
    name = models.CharField(_('Name'), max_length=25)
    symbol = models.CharField(_('Symbol'), max_length=1, blank=True, null=True)
    is_default = models.BooleanField(_('Default'), default=False,
        help_text=_('Make this the default currency.'))

    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')
        ordering = ('code',)

    def __unicode__(self):
        return self.code

    def save(self, **kwargs):
        if self.is_default:
            try:
                default_currency = Currency.objects.get(is_default=True)
            except self.DoesNotExist:
                pass
            else:
                default_currency.is_default = False
                default_currency.save()
        super(Currency, self).save(**kwargs)

    def current_rate(self):
        try:
            return self.rates.latest('date').rate
        except ExchangeRate.DoesNotExist:
            return None


class ExchangeRate(models.Model):
    currency = models.ForeignKey(Currency, related_name='rates')
    date = models.DateField(_('Date'), default=datetime.date.today)
    rate = models.DecimalField(_('Rate'), max_digits=12, decimal_places=6)
    created = models.DateTimeField(_('Created'), auto_now=True)

    class Meta:
        verbose_name = _('Exchange rate')
        verbose_name_plural = _('Exchange rates')
        unique_together = (('currency', 'date'),)
        ordering = ('-date', 'currency__code')

    def __unicode__(self):
        return "%s %s" % (self.currency, self.rate)
