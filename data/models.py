from django.db import models
from data.utils import CoinAPI
import pandas as pd

# Create your models here.
class Asset(models.Model):
    ticker = models.CharField(max_length=100)
    name = models.CharField(max_length=100, default='')

    def __str__(self):
        return '{name}({ticker})'.format(name=self.name, ticker=self.ticker)


class Marketdata(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    date = models.DateField()
    price = models.FloatField(default=0)
    nshares = models.BigIntegerField(default=0)
    tradable = models.BooleanField(default=True)
    amount = models.BigIntegerField(default=0)

    def __str__(self):
        return '{name} {date}'.format(name=self.asset.name, date=self.date)


class Coin(models.Model):
    symbol = models.CharField(max_length=50)
    ccy = models.CharField(max_length=50)
    exchange = models.CharField(max_length=50)
    time = models.DateTimeField()
    close = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    open = models.FloatField()
    volume = models.FloatField()
    amount = models.FloatField()

    def __str__(self):
        return '{time} {symbol}/{ccy} {exchange}'.format(time=self.time, symbol=self.symbol, ccy=self.ccy, exchange=self.exchange)

    @classmethod
    def update(cls, *, symbol, ccy, exchange):
        objs = cls.objects.filter(symbol=symbol, ccy=ccy, exchange=exchange)

        if len(objs) == 0:
            utc_from = None

        else:
            last_updated = objs.latest('time').time
            tobe_updated = pd.Timestamp.utcnow().floor('h') + pd.Timedelta(-1, unit='h')

            if last_updated == tobe_updated:
                print('fully updated already')
                return

            utc_from = last_updated + pd.Timedelta(1, unit='s')


        coinapi = CoinAPI(symbol=symbol, ccy=ccy, exchange=exchange)
        results = coinapi.market_history(utc_from=utc_from)
        bulk_update = []
        
        for k,v in results.items():
            obj = cls()
            obj.symbol = symbol.upper()
            obj.ccy = ccy.upper()
            obj.exchange = exchange.lower()
            obj.time = k + '+00:00'
            obj.close = v['close']
            obj.high = v['high']
            obj.low = v['low']
            obj.open = v['open']
            obj.volume = v['volumefrom']
            obj.amount = v['volumeto']
            bulk_update.append(obj)

        cls.objects.bulk_create(bulk_update)
