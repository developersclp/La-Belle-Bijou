from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from products.models import Produto, Categoria, MovimentacaoEstoque
from accounts.models import CustomUser
from orders.models import Pedido, ItemPedido
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from django.conf import settings
import requests
from .forms import ProdutoForm, ImagemProdutoFormSet, CategoriaForm, MovimentacaoEstoqueForm, UsuarioForm, PedidoForm
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Produtos =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class ListaProdutosAdm(LoginRequiredMixin, UserPassesTestMixin, ListView): 
    model = Produto 
    template_name = "dashboard/adm_produto.html" 
    context_object_name = "produtos"
    ordering = ['id']

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self): # método padrão do django para filtragem
        queryset = super().get_queryset()

        status = self.request.GET.get('status')
        pesquisa = self.request.GET.get('pesquisa')

        if status == 'ativo':
            queryset = queryset.filter(is_active=True)
        elif status == 'inativo':
            queryset = queryset.filter(is_active=False)

        if pesquisa:
            queryset = queryset.filter(nome__icontains=pesquisa)

        return queryset


class CriarProduto(LoginRequiredMixin, UserPassesTestMixin, CreateView): # view para criação de produtos
    model = Produto
    form_class = ProdutoForm # formulário a ser renderizado
    template_name = "dashboard/criar_produto.html"

    def get_context_data(self, **kwargs): # método padrão do Django que é chamado toda vez que o template é renderizado
        data = super().get_context_data(**kwargs) # pega o contexto padrão (já contém o form de ProdutoForm) e adiciona o formset(formulários de imagens)
        if self.request.POST:
            data["formset"] = ImagemProdutoFormSet(self.request.POST, self.request.FILES) # Cria o formset já preenchido com os dados enviados e com os arquivos enviados
        else: 
            data["formset"] = ImagemProdutoFormSet() # se for uma requisição GET (primeiro acesso a página) croa o formulário vazio
        return data

    def form_valid(self, form): # método padrão do Django que é chamado toda vez que o formulário é submetido
        context = self.get_context_data() # pega o form e o formset preenchidos
        formset = context["formset"]

        if form.is_valid() and formset.is_valid():
            self.object = form.save()              # salva o produto
            formset.instance = self.object         # liga imagens ao produto recém-criado
            formset.save()                         # salva imagens
            return redirect("produtos-adm")        # redireciona
        else:
            return self.form_invalid(form) # se não for válido chama a função com os erros dos formulários
        
    def test_func(self):
        return self.request.user.is_superuser


class UpdateProduto(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Produto
    form_class = ProdutoForm
    template_name = "dashboard/criar_produto.html"

    def get_context_data(self, **kwargs):
        # Pega o contexto padrão (form já carregado com dados do produto)
        data = super().get_context_data(**kwargs)

        if self.request.POST:
            # Se o formulário foi enviado, passa também os arquivos (imagens novas) e associa ao produto
            data["formset"] = ImagemProdutoFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            # Primeira vez carregando a página (GET), carrega com as imagens já salvas
            data["formset"] = ImagemProdutoFormSet(instance=self.object)

        return data

    def form_valid(self, form):
        # Pega o form principal (produto) e o formset (imagens)
        context = self.get_context_data()
        formset = context["formset"]

        if form.is_valid() and formset.is_valid():
            self.object = form.save()  # salva produto atualizado
            formset.instance = self.object
            formset.save()  # salva mudanças nas imagens (add/delete)
            return redirect("produtos-adm")
        else:
            return self.form_invalid(form)
    
    def test_func(self):
        return self.request.user.is_superuser
    

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Categorias =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class ListarCategorias(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Categoria
    template_name = "dashboard/adm_categoria.html"
    context_object_name = "categorias"
    ordering = ['id']

    def test_func(self):
        return self.request.user.is_superuser
    
    def get_queryset(self): # método padrão do django para filtragem
        queryset = super().get_queryset()

        pesquisa = self.request.GET.get('pesquisa')

        if pesquisa:
            queryset = queryset.filter(nome__icontains=pesquisa)

        return queryset
    
class CriarCategoria(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Categoria
    template_name = "dashboard/criar_categoria.html"
    form_class = CategoriaForm
    success_url = reverse_lazy("categorias-adm")

    def test_func(self):
        return self.request.user.is_superuser

class UpdateCategoria(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Categoria
    template_name = "dashboard/criar_categoria.html"
    form_class = CategoriaForm
    success_url = reverse_lazy("categorias-adm")

    def test_func(self):
        return self.request.user.is_superuser

class DeletarCategoria(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Categoria
    template_name = "dashboard/deletar_categoria.html" 
    success_url = reverse_lazy("categorias-adm")

    def test_func(self):
        return self.request.user.is_superuser
    

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Estoque =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class EntradaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = MovimentacaoEstoque
    form_class = MovimentacaoEstoqueForm
    template_name = "dashboard/movimentacao_estoque.html"
    success_url = reverse_lazy("produtos-adm")

    def get_form_kwargs(self): # função padrão do django que manda o dicionario(kwargs) com todas as informações para iniciar o form
        kwargs = super().get_form_kwargs() # puxa o método da classe mãe(CreateView) que retorna todas as informações necessárias para iniciar o form
        kwargs["tipo_movimentacao"] = "entrada" # adiciona o campo "tipo_movimentação = saida" no kwargs
        return kwargs # manda o kwargs atualizado para o form

    def get_context_data(self, **kwargs): # função padrão do django que manda o dicionario(kwargs) com todas as informações a serem usadas no template
        context = super().get_context_data(**kwargs) # puxa o método da classe mãe(CreateView) que retorna todas as informações necessárias para para o template
        context["tipo_movimentacao"] = "entrada" # adiciona o campo "tipo_movimentação = saida" no context
        return context # manda o context atualizado para o template

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        form.instance.tipo = "ENTRADA"
        return super().form_valid(form)
    
    def test_func(self):
        return self.request.user.is_superuser


class SaidaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = MovimentacaoEstoque
    form_class = MovimentacaoEstoqueForm
    template_name = "dashboard/movimentacao_estoque.html"
    success_url = reverse_lazy("produtos-adm")

    def get_form_kwargs(self): # função padrão do django que manda o dicionario(kwargs) com todas as informações para iniciar o form
        kwargs = super().get_form_kwargs() # puxa o método da classe mãe(CreateView) que retorna todas as informações necessárias para iniciar o form
        kwargs["tipo_movimentacao"] = "saida" # adiciona o campo "tipo_movimentação = saida" no kwargs
        return kwargs # manda o kwargs atualizado para o form

    def get_context_data(self, **kwargs): # função padrão do django que manda o dicionario(kwargs) com todas as informações a serem usadas no template
        context = super().get_context_data(**kwargs) # puxa o método da classe mãe(CreateView) que retorna todas as informações necessárias para para o template
        context["tipo_movimentacao"] = "saida" # adiciona o campo "tipo_movimentação = saida" no context
        return context # manda o context atualizado para o template

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        form.instance.tipo = "SAIDA"
        return super().form_valid(form)
    
    def test_func(self):
        return self.request.user.is_superuser
    

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Usuários =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class ListaUsuarios(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = 'dashboard/adm_usuarios.html'
    context_object_name = 'usuarios'
    ordering = ['id']

    def test_func(self):
        return self.request.user.is_superuser
    
    def get_queryset(self): # método padrão do django para filtragem
        queryset = super().get_queryset()

        status = self.request.GET.get('status')
        pesquisa = self.request.GET.get('pesquisa')

        if status == 'ativo':
            queryset = queryset.filter(is_active=True)
        elif status == 'inativo':
            queryset = queryset.filter(is_active=False)

        if pesquisa:
            queryset = queryset.filter(username__icontains=pesquisa)

        return queryset
    
class DetalheUsuario(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = CustomUser
    template_name = "dashboard/detalhe_usuario.html"
    context_object_name = "usuario"

    def test_func(self):
        return self.request.user.is_superuser
    
class EditarUsuario(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CustomUser
    form_class = UsuarioForm
    template_name = "dashboard/editar_usuario.html"
    success_url = reverse_lazy("usuarios-adm")

    def test_func(self):
        return self.request.user.is_superuser

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-= Pedidos =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

class ListaPedidos(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Pedido
    template_name = "dashboard/adm_pedidos.html"
    context_object_name = "pedidos"
    ordering = ["id"]

    def get_queryset(self): # método padrão do django para filtragem
        queryset = super().get_queryset()

        status = self.request.GET.get('status')
        pesquisa = self.request.GET.get('pesquisa')

        if status == 'Pendente':
            queryset = queryset.filter(status="PENDENTE")
        elif status == 'Pago':
            queryset = queryset.filter(status="PAGO")
        elif status == 'Cancelado':
            queryset = queryset.filter(status="CANCELADO")
        elif status == 'Aguardando Pagamento':
            queryset = queryset.filter(status="AGUARDANDO_PAGAMENTO")

        if pesquisa:
            queryset = queryset.filter(id__istartswith=pesquisa)

        return queryset

    def test_func(self):
        return self.request.user.is_superuser
    
class EditarPedido(UpdateView):
    model = Pedido
    form_class = PedidoForm
    template_name = "dashboard/editar_pedido.html"
    context_object_name = "pedido"
    success_url = "pedidos-adm"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["itens_pedido"] = ItemPedido.objects.filter(pedido=self.object)
        return context
    
class GerarEtiquetaView(View):
    def post(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk)

        # Se já existir etiqueta, não gerar de novo
        if pedido.etiqueta_gerada:
            messages.info(request, "A etiqueta já foi gerada para este pedido.")
            return redirect("editar-pedido", pedido.pk)

        try:
            self.gerar_superfrete(pedido)
            messages.success(request, "Etiqueta gerada com sucesso!")
            print("Etiqueta gerada com sucesso!")
            return redirect("home")
        except Exception as e:
            print("ERRO AO GERAR ETIQUETA:", e)
            messages.error(request, "Erro ao gerar etiqueta. Veja os logs.")
        
        return redirect("editar-pedido", pedido.pk)

    def gerar_superfrete(self, pedido):
        endereco = pedido.endereco
        usuario = pedido.usuario

        total_peso = 0
        max_altura = 0
        max_largura = 0
        max_comprimento = 0

        for item in pedido.itens.all():
            peso = float(item.produto.peso or 0) * item.quantidade
            total_peso += peso

            max_altura = max(max_altura, float(item.produto.altura or 0))
            max_largura = max(max_largura, float(item.produto.largura or 0))
            max_comprimento = max(max_comprimento, float(item.produto.comprimento or 0))
        
        valor_total_produtos = sum(
            float(item.preco_unitario) * item.quantidade
            for item in pedido.itens.all()
        )

        payload = {
            "service": pedido.frete_servico_id,
            "from": {
                "name": "Sarah Suelen Fernandes Freitas",
                "postal_code": "01024-000",
                "address": "Rua da Cantareira",
                "number": "686",
                "district": "Centro",
                "city": "São Paulo",
                "state_abbr": "SP"
            },
            "to": {
                'name': f"{usuario.first_name} {usuario.last_name}",
                'document': usuario.cpf,
                "postal_code": endereco.cep,
                "address": endereco.rua,
                "number": endereco.numero,
                "district": endereco.bairro,
                "city": endereco.cidade,
                "state_abbr": endereco.estado,
                "email": usuario.email
            },
            "products": [
                {
                    "name": item.produto.nome,
                    "quantity": item.quantidade,
                    "unitary_value": float(item.preco_unitario)
                }
                for item in pedido.itens.all()
            ],
            "volumes": [
                {
                    "weight": total_peso,
                    "width": max_largura,
                    "height": max_altura,
                    "length": max_comprimento
                }
            ],
            "options": {
                "insurance_value": float(valor_total_produtos)
            },
            "platform": "labellebijou"
        }

        print("PAYLOAD:", payload)

        teste={
                "accept": "application/json",
                "User-Agent": "Labellebijou/1.0 (labellebijoo@gmail.com)",
                "Authorization": f"Bearer {settings.SUPERFRETE_API_KEY}",
                "Content-Type": "application/json"
            }
        
        print(teste)

        # Criando carrinho
        response = requests.post(
            "https://api.superfrete.com/api/v0/cart",
            json=payload,
            headers={
                "accept": "application/json",
                "User-Agent": "Labellebijou/1.0 (labellebijoo@gmail.com)",
                "Authorization": f"Bearer {settings.SUPERFRETE_API_KEY}",
                "Content-Type": "application/json"
            }
        )

        print("STATUS CART:", response.status_code)
        print("RAW CART RESPONSE:", response.text)

        if response.status_code not in (200, 201):
            raise Exception(f"Erro CART: {response.status_code} - {response.text}")

        data = response.json()
        cart_token = data.get("token")

        print("CART TOKEN:", cart_token)

        # Gerando etiqueta
        purchase = requests.post(
            f"https://api.superfrete.com/api/v0/cart/{cart_token}/purchase",
            headers={
                "Authorization": f"Bearer {settings.SUPERFRETE_API_KEY}",
                "Content-Type": "application/json"
            }
        )

        print("STATUS PURCHASE:", purchase.status_code)
        print("RAW PURCHASE RESPONSE:", purchase.text)

        if purchase.status_code not in (200, 201):
            raise Exception(f"Erro PURCHASE: {purchase.status_code} - {purchase.text}")

        purchase_data = purchase.json()

        pedido.codigo_rastreio = purchase_data.get("tracking_code")
        pedido.etiqueta_url = purchase_data.get("label_url")
        pedido.etiqueta_gerada = True
        pedido.save()
