import requests, base64
from decimal import Decimal
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.utils import timezone

from accounts.models import Endereco
from products.models import Produto
from .models import Pedido, ItemPedido
from products.cart import Cart
from accounts.forms import EnderecoForm


class CheckoutView(View):
    template_name = "orders/checkout.html"

    def get(self, request):
        cart = Cart(request)
        if not len(cart):
            messages.error(request, "Seu carrinho está vazio.")
            return redirect("ver_carrinho")
        else:
            endereco_form = EnderecoForm()
            return render(request, self.template_name, {"cart": cart, "endereco": endereco_form})

    def post(self, request):
        cart = Cart(request)
        endereco_form = EnderecoForm(request.POST)

        if not len(cart):
            messages.error(request, "Seu carrinho está vazio.")
            return redirect("ver_carrinho")
        
        
        if endereco_form.is_valid():
            endereco_data = endereco_form.cleaned_data
            endereco, created = Endereco.objects.get_or_create(
                usuario=request.user,
                rua=endereco_data["rua"],
                numero=endereco_data["numero"],
                complemento=endereco_data.get("complemento", ""),
                cep=endereco_data["cep"],
            )
        else:
            messages.error(request, "Endereço inválido.")
            return redirect("checkout")
        
        pedido = Pedido.objects.create(
            usuario=request.user,
            endereco=endereco,
            status="PENDENTE",
            valor_total=cart.get_total_price(),
            data_criacao=timezone.now(),
        )

        for item in cart:
            produto = Produto.objects.get(id=item["id"])
            ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                quantidade=item["quantidade"],
                preco_unitario=item["preco"],
            )
        
        payload = {
            "is_building": False,
            "type": "order",
            "payment_settings": {
                "accepted_payment_methods": ["pix", "credit_card", "boleto"],
                "pix_settings": {"expires_in": 3600, "discount_percentage": 0},
                "credit_card_settings": {
                    "operation_type": "auth_and_capture",
                    "installments_setup": {
                        "interest_type": "simple",
                        "interest_rate": 0,
                        "amount": int(cart.get_total_price() * 100),
                        "max_installments": 12,
                        "min_installments": 1
                    }
                },
                "boleto_settings": {
                    "instructions": "Pague o boleto até o vencimento.",
                    "due_in": 2,
                    "discount_percentage": 0,
                }
            },
            "customer_settings": {
                "customer": {
                    "name": request.user.get_full_name() or request.user.username or "Cliente",
                    "email": request.user.email or "sem-email@example.com",
                    "type": "individual",
                    "document": getattr(request.user, "cpf", None) or "00000000000",
                    "phone": getattr(request.user, "telefone", None) or "+5511999999999"
                }
            },
            "cart_settings": {
                "items": [
                    {
                        "name": item["nome"],
                        "amount": int(Decimal(item["preco"]) * 100),
                        "default_quantity": item["quantidade"]
                    }
                    for item in cart
                ]
            }
        }

        auth = base64.b64encode(f"{settings.PAGARME_API_KEY}:".encode()).decode()

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Basic {auth}"
        }

        response = requests.post(
            f"{settings.PAGARME_API_URL}/paymentlinks",
            json=payload,
            headers=headers,
        )
        data = response.json()
        print("STATUS CODE:", response.status_code)
        print("RESPONSE JSON:", data)
        
        if response.status_code in (200, 201):
            link_pagamento = data.get("url")
            if link_pagamento:
                # limpa o carrinho e atualiza status do pedido
                cart.clear()
                pedido.status = "AGUARDANDO_PAGAMENTO"
                pedido.payment_url = link_pagamento  # se tiver campo no model, armazene
                pedido.save()

                # redireciona cliente para a página de checkout hospedada
                return redirect(link_pagamento)
            else:
                messages.error(request, f"Resposta inesperada da API: {data}")
                pedido.status = "CANCELADO"
                pedido.save()
                return redirect("checkout")
        else:
            messages.error(request, f"Erro ao criar pagamento: {data}")
            pedido.status = "CANCELADO"
            pedido.save()
            return redirect("checkout")