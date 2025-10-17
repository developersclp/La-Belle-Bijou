from django.shortcuts import render
from django.views.generic import DetailView, TemplateView
from .models import Produto, Categoria

# Create your views here.
class Home(TemplateView):
    template_name = "products/home.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)

        produtos_mais_vendidos = Produto.objects.mais_vendidos(10)
        contexto['produtos_mais_vendidos'] = produtos_mais_vendidos

        categorias = Categoria.objects.all().prefetch_related('produtos')
        contexto['categorias'] = categorias

        for categoria in categorias:
            produtos_count = categoria.produtos.count()

        # Criar lista de tuplas (categoria, produtos) para o template
        categorias_com_produtos = []
        for categoria in categorias:
            produtos_da_categoria = categoria.produtos.all() # Limita a 10 produtos
            categorias_com_produtos.append((categoria, produtos_da_categoria))
        contexto['categorias_com_produtos'] = categorias_com_produtos

        return contexto

class DetailProduto(DetailView):
    model = Produto
    template_name = "products/detalhe_produto.html"
    context_object_name = "produto"

def teste_carrinho(request):
    return render(request, "products/teste_carrinho.html")