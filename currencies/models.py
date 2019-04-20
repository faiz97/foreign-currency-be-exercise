from django.db import models

# Create your models here.
class Currency(models.Model):
    currency_id = models.AutoField(primary_key=True)
    domain = models.CharField(max_length=3, blank=False)
    codomain = models.CharField(max_length=3, blank=False)

    class Meta:
        ordering = ('currency_id',)
        unique_together = ('domain', 'codomain',)

class CurrencyRate(models.Model):
    currency_rate_id = models.AutoField(primary_key=True)
    currency_id = models.ForeignKey(Currency, on_delete=models.CASCADE, db_column='currency_id')
    rate = models.FloatField()
    date = models.DateField()

    class Meta:
        ordering = ('currency_id', 'date',)
        unique_together = ('currency_id', 'date',)


