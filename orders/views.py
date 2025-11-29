import requests, base64, json
from decimal import Decimal
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin

from accounts.models import Endereco
from products.models import Produto, MovimentacaoEstoque
from .models import Pedido, ItemPedido
from products.cart import Cart
from accounts.forms import EnderecoForm

from .models import Pedido

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Frete =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class CalcularFreteView(LoginRequiredMixin, View):
    template_name = "orders/calcular-frete.html"

    def get(self, request):
        cart = Cart(request)
        if not len(cart):
            messages.error(request, "Seu carrinho está vazio.")
            return redirect("ver_carrinho")
        endereco_form = EnderecoForm()
        return render(request, self.template_name, {"cart": cart, "endereco": endereco_form})

    def post(self, request, *args, **kwargs):
        try:
            cart = Cart(request)
            endereco_form = EnderecoForm(request.POST)

            if not len(cart):
                messages.error(request, "Seu carrinho está vazio.")
                return redirect("ver_carrinho")

            if endereco_form.is_valid():
                endereco_data = endereco_form.cleaned_data
                cep_destino = endereco_data["cep"]
            else:
                messages.error(request, "Endereço inválido.")
                return redirect("calcular-frete")

            cep_origem = "01001-000"

            produtos = []
            for item in cart:
                produto = Produto.objects.get(id=item["id"])
                produtos.append({
                    "weight": float(produto.peso),
                    "width": float(produto.largura),
                    "height": float(produto.altura),
                    "length": float(produto.comprimento),
                    "quantity": item["quantidade"]
                })

            payload = {
                "from": {"postal_code": cep_origem},
                "to": {"postal_code": cep_destino},
                "services": "1,2,17,3,31",
                "options": {"insurance_value": float(cart.get_total_price())},
                "products": produtos
            }

            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.SUPERFRETE_API_KEY}"
            }

            response = requests.post(settings.SUPERFRETE_API_URL, json=payload, headers=headers)

            if response.status_code != 200:
                messages.error(request, "Erro ao consultar API do SuperFrete.")
                return redirect("calcular-frete")

            data = response.json()
            servicos = data.get("data") if isinstance(data, dict) else data

            opcoes_envio = []
            for servico in servicos or []:
                if servico.get("price") == None:
                    continue
                else:
                    opcoes_envio.append({
                        "id": servico.get("id"),                       # <--- ESSENCIAL!!
                        "nome": servico.get("company", {}).get("name"),
                        "servico": servico.get("name"),
                        "valor": servico.get("price"),
                        "prazo": servico.get("delivery_time"),
                        "logo": servico.get("company", {}).get("picture")
                    })
            print(opcoes_envio)

            request.session["opcoes_envio"] = opcoes_envio
            request.session["endereco"] = {
                "rua": endereco_data["rua"],
                "numero": endereco_data["numero"],
                "complemento": endereco_data.get("complemento", ""),
                "cep": endereco_data["cep"],
            }
            request.session.modified = True

            return render(request, self.template_name, {
                "cart": cart,
                "endereco": endereco_form,
                "opcoes_envio": opcoes_envio
            })

        except Exception as e:
            messages.error(request, f"Erro ao calcular frete: {e}")
            return redirect("calcular-frete")
        
class EscolherFreteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        frete_valor = request.POST.get("frete_escolhido")
        servico_nome = request.POST.get("servico_nome")
        servico_id = request.POST.get("servico_id")

        if not frete_valor or not servico_id:
            messages.error(request, "Selecione uma opção de frete.")
            return redirect("calcular-frete")

        request.session["frete_escolhido"] = float(frete_valor)
        request.session["frete_servico"] = servico_nome
        request.session["frete_servico_id"] = servico_id
        request.session.modified = True

        return redirect("checkout")
        
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Pagarme =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class CheckoutView(LoginRequiredMixin, View):
    template_name = "orders/checkout.html"

    def get(self, request):
        cart = Cart(request)
        if not len(cart):
            messages.error(request, "Seu carrinho está vazio.")
            return redirect("ver_carrinho")

        frete_valor = request.session.get("frete_escolhido", 0)
        frete_servico = request.session.get("frete_servico", "Não selecionado")
        endereco = request.session.get("endereco", None)
        total_com_frete = cart.get_total_price() + Decimal(frete_valor)

        context = {
            "cart": cart,
            "frete_valor": frete_valor,
            "frete_servico": frete_servico,
            "total_com_frete": total_com_frete,
            "endereco": endereco,
        }

        return render(request, self.template_name, context)
    
    def post(self, request):
        cart = Cart(request)
        endereco_data = request.session.get("endereco")
        frete_valor = Decimal(request.session.get("frete_escolhido", 0))
        frete_servico = request.session.get("frete_servico", "Não selecionado")

        if not len(cart):
            messages.error(request, "Seu carrinho está vazio.")
            return redirect("ver_carrinho")

        if endereco_data:
            endereco, created = Endereco.objects.get_or_create(
                usuario=request.user,
                rua=endereco_data["rua"],
                numero=endereco_data["numero"],
                complemento=endereco_data.get("complemento", ""),
                cep=endereco_data["cep"],
            )
        else:
            messages.error(request, "Endereço não encontrado. Volte e preencha novamente.")
            return redirect("calcular-frete")

        total_com_frete = cart.get_total_price() + frete_valor

        frete_id = request.session.get("frete_servico_id")

        pedido = Pedido.objects.create(
                usuario=request.user,
                endereco=endereco,
                status="PENDENTE",
                valor_total=total_com_frete,
                frete_servico_id=frete_id,   # <--- ESSENCIAL!
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
        
        itensCarrinho =  [{
                            "name": item["nome"],
                            "amount": int(Decimal(item["preco"]) * 100),
                            "default_quantity": item["quantidade"] } 
                            for item in cart
                        ]
        
        frete = {
                 "name": f"Frete - {frete_servico}", 
                 "amount": int(round(frete_valor, 2) * 100),
                 "default_quantity": 1
                }
        
        itensCarrinho.append(frete)
        
        payload = {
            "is_building": False,
            "type": "order",
            "max_paid_sessions": 1,
            "payment_settings": {
                "accepted_payment_methods": ["pix", "credit_card", "boleto"],
                "pix_settings": {"expires_in": 3600, "discount_percentage": 0},
                "credit_card_settings": {
                    "operation_type": "auth_and_capture",
                    "installments_setup": {
                        "interest_type": "simple",
                        "interest_rate": 0,
                        "amount": int(total_com_frete * 100),
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
                "items": itensCarrinho
            },
            "metadata": { "pedido_id": pedido.id }
        }

        print(payload)

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
            pagarme_order_id = data.get("id")
            if link_pagamento:
                # limpa o carrinho e atualiza status do pedido
                cart.clear()
                pedido.status = "AGUARDANDO_PAGAMENTO"
                pedido.payment_url = link_pagamento
                if pagarme_order_id:
                    pedido.pagarme_id = pagarme_order_id
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
        


@method_decorator(csrf_exempt, name="dispatch")
class PagarmeWebhookView(View):
    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body)
            event_type = payload.get("type")
            order_data = payload.get("data", {})
        except json.JSONDecodeError:
            return JsonResponse({"message": "JSON inválido"}, status=200)

        paymentlink_code = (
            order_data.get("integration", {}).get("code")
            or order_data.get("code")
            or order_data.get("charges", [{}])[0].get("code")
        )

        if not paymentlink_code:
            return JsonResponse({"message": "Order ID ausente"}, status=200)

        pedido = Pedido.objects.filter(pagarme_id=paymentlink_code).first()

        if not pedido:
            return JsonResponse({"message": "Pedido não encontrado"}, status=200)

        # Atualizar endereço vindo da pagarme
        pagarme_address = (
            order_data.get("customer", {}).get("address")
            or order_data.get("charges", [{}])[0]
                .get("customer", {})
                .get("address", {})
        )

        cidade = pagarme_address.get("city")
        estado = pagarme_address.get("state")

        endereco = pedido.endereco
        if cidade:
            endereco.cidade = cidade
        if estado:
            endereco.estado = estado
        endereco.save()

        # STATUS PAID
        if event_type in ["order.paid", "payment.paid"]:
            pedido.status = "PAGO"
            pedido.data_pagamento = timezone.now()
            pedido.save()

            # Baixa estoque
            for item in pedido.itens.all():
                MovimentacaoEstoque.objects.create(
                    produto=item.produto,
                    tipo="SAIDA",
                    quantidade=item.quantidade,
                    motivo="VENDA",
                    usuario=pedido.usuario
                )

        # STATUS CANCELLED
        elif event_type in [
            "order.canceled",
            "payment.canceled",
            "order.closed",
            "order.payment_failed",
            "payment.failed",
        ]:
            pedido.status = "CANCELADO"
            pedido.save()

        return JsonResponse({"message": "Webhook processado"}, status=200)