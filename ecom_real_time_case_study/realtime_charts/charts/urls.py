from django.urls import path

from .views import index, get_filter_options, salesby_chart

urlpatterns = [
    path('', index),
    path('chart/filter-options/', get_filter_options, name='chart-filter-options'),
    path('chart/sales-by/<str:salesby>/', salesby_chart, name='chart-sales-by'),
]