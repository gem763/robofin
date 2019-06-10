# from django.shortcuts import render
from rest_framework import viewsets
from .serializers import get_assetSerializer, get_marketdataSerializer
from data.models import Asset, Marketdata
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


class AssetView2(generics.ListAPIView):
    serializer_class = get_assetSerializer()

    def get_queryset(self):
        queryset = Asset.objects.all()

        tickers = self.request.query_params.get('ticker', None)
        names = self.request.query_params.get('name', None)

        if (tickers is not None) and (names is None):
            queryset = queryset.filter(ticker__in=tickers.split(','))

        elif (tickers is None) and (names is not None):
            queryset = queryset.filter(name__in=names.split(','))

        print('*******************************', len(queryset))
        return queryset.order_by('ticker')


class AssetView(generics.ListAPIView):
    serializer_class = get_assetSerializer()
    # pagination_class = None
    queryset = Asset.objects.all()

    def list(self, request, *args, **kwargs):
        self.queryset = self._queryset()

        # if len(self.get_queryset())<100:
        #     self.pagination_class = None

        return super().list(request, args, kwargs)

        # queryset = self._queryset()
        # serializer = self.serializer_class(queryset, many=True)
        # return Response(serializer.data)


    # ************** 중요 **************
    # get_queryset(self)를 오버라이딩 해서 쓰지말자,
    # get_queryset은 항상 두번씩 불러지기 때문에 비효율적인듯 (form 생성할때 한번더 부른다고는 하는데 잘 이해안감..)

    def _queryset(self):
        qs = self.get_queryset()
        ticker = self.request.query_params.get('ticker', None)
        name = self.request.query_params.get('name', None)

        if (ticker is not None):
            qs = qs.filter(ticker__icontains=ticker)

        if (name is not None):
            qs = qs.filter(name__icontains=name)

        return qs.order_by('ticker')


class MarketdataView(generics.ListAPIView):
    serializer_class = None
    queryset = Marketdata.objects.all()

    _flds = ['ticker', 'date']
    _items = None
    _tickers = None

    def _queryset(self):
        qs = self.get_queryset()
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        tickers = self.request.query_params.get('ticker', None)
        items = self.request.query_params.get('item', None)

        if start is not None:
            qs = qs.filter(date__gte=start)

        if end is not None:
            qs = qs.filter(date__lte=end)

        if tickers is not None:
            self._tickers = tickers.split(',')
            qs = qs.filter(asset__ticker__in=self._tickers)
        else:
            self._tickers = sorted(list(set(qs.values_list('asset__ticker', flat=True))))

        if items is None:
            self.serializer_class = get_marketdataSerializer()
        else:
            self._items = items.split(',')
            flds = self._flds + self._items
            self.serializer_class = get_marketdataSerializer(flds)

        # print('*************************', len(self._tickers))
        return qs.order_by('date')


    def list(self, request, *args, **kwargs):
        self.queryset = self._queryset()
        response = super().list(request, args, kwargs)
        # results_0 = response.data['results']
        # results = {tick:OrderedDict() for tick in self._tickers}

        # serializer = self.serializer_class(self.queryset, many=True)

        # if (self._items is not None) and (len(self._items)==1):
        #     item = self._items[0]
        #     for res in results_0:
        #         ticker = res.pop('ticker', None)
        #         date = res.pop('date', None)
        #         results[ticker][date] = res[item]
        #
        # else:
        #     for res in results_0:
        #         ticker = res.pop('ticker', None)
        #         date = res.pop('date', None)
        #         results[ticker][date] = res

        # response.data['results'] = results

        print('***************************', self.queryset)
        print('***************************', len(self.queryset))
        print('***************************', len(response.data['results']))
        print('***************************', response.data['results'])
        return response
        # return Response(serializer.data)



class MarketdataView2(generics.ListAPIView):
    _flds = ['ticker', 'date']
    _items = None
    _tickers = None

    def get_queryset(self):
        queryset = Marketdata.objects.all()

        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        tickers = self.request.query_params.get('ticker', None)
        items = self.request.query_params.get('item', None)


        if start is not None:
            queryset = queryset.filter(date__gte=start)

        if end is not None:
            queryset = queryset.filter(date__lte=end)

        if tickers is not None:
            self._tickers = tickers.split(',')
            queryset = queryset.filter(asset__ticker__in=self._tickers)
        else:
            self._tickers = sorted(list(set(queryset.values_list('asset__ticker', flat=True))))

        if items is None:
            self.serializer_class = get_marketdataSerializer()
        else:
            self._items = items.split(',')
            flds = self._flds + self._items
            self.serializer_class = get_marketdataSerializer(flds)

        print('*************************', len(self._tickers))
        return queryset.order_by('date')


    def list(self, request, *args, **kwargs):
        print('------------------------1')
        response = super().list(request, args, kwargs)
        print('------------------------2')
        results_0 = response.data['results']
        results = {tick:OrderedDict() for tick in self._tickers}

        # if (self._items is not None) and (len(self._items)==1):
        #     item = self._items[0]
        #     for res in results_0:
        #         ticker = res.pop('ticker', None)
        #         date = res.pop('date', None)
        #         results[ticker][date] = res[item]
        #
        # else:
        #     for res in results_0:
        #         ticker = res.pop('ticker', None)
        #         date = res.pop('date', None)
        #         results[ticker][date] = res

        response.data['results'] = self._tickers #results
        return response
