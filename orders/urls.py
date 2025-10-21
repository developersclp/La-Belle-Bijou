from django.urls import path
from .views import *

urlpatterns = [
    path("checkout/pix/", CheckoutPixView.as_view(), name="checkout_pix"),
]