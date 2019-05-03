from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from backtester.utils import backtest, 매출상위, 시총상위PB저평가, 슈퍼밸류, get_fisyear
# from backtester import utils
import inspect
import traceback
import re


model_matcher = {
    0: {'model':매출상위, 'desc':'매출액이 큰 종목'},
    1: {'model':시총상위PB저평가, 'desc':'시가총액 상위종목 중 PBR이 낮은 종목'},
    2: {'model':슈퍼밸류, 'desc':'순익,자본,OCF,EBITDA,배당>0 이면서 PER,PBR,PCR,PSR,EV/EBITDA가 낮은 종목'},
}


def dashboard(request):
    return render(request, 'backtester/dashboard.html', {'model_matcher':model_matcher})


def get_results(model, n):
    bt = backtest(model, n)
    navs = bt.navs()
    navs_model = list(navs['Model'].values)
    navs_bm = list(navs['BM'].values)
    navs_min = max(round(navs.min().min(), 1) - 0.1, 0)
    stats = bt.stats().T.to_dict('split')
    dates = list(navs.index.date.astype(str))
    pos = bt.position_mapped()
    results = {'navs_model':navs_model, 'navs_bm':navs_bm, 'dates':dates, 'navs_min':navs_min, 'stats':stats, 'pos':pos}
    return results

class GetSourceView(View):
    def get(self, request):
        model_id = request.GET.get('model_id', None)

        if model_id is not None:
            source = inspect.getsource(model_matcher[int(model_id)]['model'])
            return JsonResponse({'source':source})


class RunBacktestView(View):
    def get(self, request):
        model_id = request.GET.get('model_id', None)
        mysource = request.GET.get('mysource', None)
        n_pos = request.GET.get('n_pos', None)

        try:
            if (model_id is not None) & (n_pos is not None):
                model = model_matcher[int(model_id)]['model']
                n_pos = int(n_pos)
                results = get_results(model, n=n_pos)
                return JsonResponse(results)

            elif (mysource is not None) & (n_pos is not None):
                fname = re.findall(r'def ([^ ]+)\(', mysource)[0]
                exec(mysource, globals())
                mymodel = globals()[fname]
                results = get_results(mymodel, n=int(n_pos))
                return JsonResponse(results)

        except Exception as e:
            print('**** error : ', e)
            return JsonResponse({'error':traceback.format_exc()})
            # return JsonResponse({'error':str(e)})
