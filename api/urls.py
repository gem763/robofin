from django.urls import path, include
# from rest_framework.urlpatterns import format_suffix_patterns
from . import views as v
from rest_framework import routers

# assets = AssetView.as_view({
#     # 'post': 'create',
#     'get': 'list'
# })
#
# urlpatterns = format_suffix_patterns([
#     path('auth/', include('rest_framework.urls', namespace='rest_framework')),
#     path('assets/', assets, name='assets'),
# ])


# router = routers.DefaultRouter()
# router.register('assets', AssetView)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.

urlpatterns = [
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('', include(router.urls)),
    path('assets', v.AssetView.as_view()),
    path('assets/', v.AssetView.as_view()),
    path('marketdata/', v.MarketdataView.as_view()),
    path('marketdata', v.MarketdataView.as_view()),
    # path('test/', v.test)
]
