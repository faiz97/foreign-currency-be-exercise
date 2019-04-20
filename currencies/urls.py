from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from currencies import views

urlpatterns = [
    path('currencies/', views.CurrencyCreator.as_view(), name='currency_creator'),
    path('currencies', views.CurrencyDestroyer.as_view(), name='currency_destroyer'),
    path('currencies/list/', views.CurrencyList.as_view(), name='currency_list'),
    path('currencies/list', views.CurrencyDateList.as_view(), name='currency_date_list'),
    path('currencies/rates/', views.CurrencyRateCreator.as_view(), name='currency_rate_creator'),
    path('currencies/rates/trends', views.CurrencyRatesTrendList.as_view(), name='rates_trend'),
]

urlpatterns = format_suffix_patterns(urlpatterns)