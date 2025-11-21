from django.urls import path
from .views import *

urlpatterns = [
    path("calcular-frete/", CalcularFreteView.as_view(), name="calcular-frete"),
    path("escolher-frete/", EscolherFreteView.as_view(), name="escolher-frete"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("pagarme/webhook/", PagarmeWebhookView.as_view(), name="pagarme_webhook"),
]