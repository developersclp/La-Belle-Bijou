from django.urls import path
from .views import *

urlpatterns = [
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("pagarme/webhook/", PagarmeWebhookView.as_view(), name="pagarme_webhook"),
]