import requests
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


class CheckoutPixView(View):
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
            return redirect("checkout_pix")
        
        pedido = Pedido.objects.create(
            usuario=request.user,
            endereco=endereco,
            status="PENDENTE",
            valor_total=cart.get_total_price(),
            data_criacao=timezone.now(),
        )

        # 2️⃣ Cria os itens do pedido
        itens_pagamento = []
        for item in cart:
            produto = Produto.objects.get(id=item["id"])
            ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                quantidade=item["quantidade"],
                preco_unitario=item["preco"],
            )
            itens_pagamento.append({
                "name": item["nome"],
                "quantity": item["quantidade"],
                "amount": int(item["preco"] * 100),
            })

        # 3️⃣ Monta o payload para Pagar.me
        payload = {
            "api_key": settings.PAGARME_API_KEY,
            "amount": int(cart.get_total_price() * 100),
            "items": itens_pagamento,
            "customer": {
                "external_id": str(request.user.id),
                "name": request.user.username,
                "email": request.user.email,
                "type": "individual",
                "country": "br",
            },
            "payment_method": "pix",
        }

        headers = {
            "Authorization": f"Bearer {settings.PAGARME_API_KEY}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                f"{settings.PAGARME_API_URL}/orders",
                json=payload,
                headers=headers,
            )
            data = response.json()
            print(data)

            if response.status_code in [200, 201]:
                qr_code = data["charges"][0]["last_transaction"]["qr_code"]
                qr_code_base64 = data["charges"][0]["last_transaction"]["qr_code_base64"]

                # limpa o carrinho
                cart.clear()

                return render(
                    request,
                    "orders/pagamento_pix.html",
                    {"pedido": pedido, "qr_code": qr_code, "qr_code_base64": qr_code_base64},
                )

            else:
                messages.error(request, f"Erro ao criar pagamento: {data}")
                pedido.status = "CANCELADO"
                pedido.save()
                return redirect("checkout_pix")

        except Exception as e:
            messages.error(request, f"Erro de conexão com o Pagar.me: {e}")
            pedido.status = "CANCELADO"
            pedido.save()
            return redirect("checkout_pix")

class Pix(View):
    template_name = 'orders/pagamento_pix.html'