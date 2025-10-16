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

        produtos_por_categoria = {}
        for categoria in categorias:
            produtos_por_categoria[categoria] = categoria.produtos.all()
        contexto['produtos_por_categoria'] = produtos_por_categoria

        produtos = Produto.objects.all()
        contexto['produtos'] = produtos
        return contexto

class DetailProduto(DetailView):
    model = Produto
    template_name = "products/detalhe_produto.html"
    context_object_name = "produto"

def teste_carrinho(request):
    return render(request, "products/teste_carrinho.html")