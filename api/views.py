# from django.shortcuts import render
from rest_framework import viewsets
from .serializers import get_assetSerializer, get_marketdataSerializer
from .models import Asset, Marketdata
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import requests
from collections import OrderedDict


def test(request):
    url = 'http://localhost:8000/api/assets'
    out = requests.get(url).json()
    # out = requests.get(url, data=data).json()
    return JsonResponse(out)


# class AssetView2(viewsets.ModelViewSet):
#     queryset = Asset.objects.all()
#     serializer_class = AssetSerializer
#     # permission_classes = (permissions.IsAuthenticated,)


class AssetView(generics.ListAPIView):
    serializer_class = get_assetSerializer()

    def get_queryset(self):
        queryset = Asset.objects.all()

        tickers = self.request.query_params.get('ticker', None)
        names = self.request.query_params.get('name', None)

        if (tickers is not None) and (names is None):
            queryset = queryset.filter(ticker__in=tickers.split(','))

        elif (tickers is None) and (names is not None):
            queryset = queryset.filter(name__in=names.split(','))

        return queryset.order_by('ticker')


class MarketdataView(generics.ListAPIView):
    _flds = ['ticker', 'date']
    _items = None
    _tickers = None

    def get_queryset(self):
        queryset = Marketdata.objects.all()

        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        tickers = self.request.query_params.get('ticker', None)
        items = self.request.query_params.get('item', None)

        if tickers is not None:
            self._tickers = tickers.split(',')
            queryset = queryset.filter(asset__ticker__in=self._tickers)

        if start is not None:
            queryset = queryset.filter(date__gte=start)

        if end is not None:
            queryset = queryset.filter(date__lte=end)

        if items is None:
            self.serializer_class = get_marketdataSerializer()
        else:
            self._items = items.split(',')
            flds = self._flds + self._items
            self.serializer_class = get_marketdataSerializer(flds)

        return queryset.order_by('date')


    def list(self, request, *args, **kwargs):
        response = super().list(request, args, kwargs)
        results_0 = response.data['results']
        results = {tick:OrderedDict() for tick in self._tickers}

        if (self._items is not None) and (len(self._items)==1):
            item = self._items[0]
            for res in results_0:
                ticker = res.pop('ticker', None)
                date = res.pop('date', None)
                results[ticker][date] = res[item]

        else:
            for res in results_0:
                ticker = res.pop('ticker', None)
                date = res.pop('date', None)
                results[ticker][date] = res

        response.data['results'] = results
        return response
