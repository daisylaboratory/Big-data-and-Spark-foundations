from django.urls import path

from .consumers import ChartsConsumer

ws_urlpatterns = [
    path('ws/charts/', ChartsConsumer.as_asgi())
]