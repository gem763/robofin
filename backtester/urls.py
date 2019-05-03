from django.urls import path
from . import views as v

urlpatterns = [
    path('', v.dashboard, name='dashboard'),
    path('run_backtest/', v.RunBacktestView.as_view(), name='run_backtest'),
    path('get_source/', v.GetSourceView.as_view(), name='get_source')
]
