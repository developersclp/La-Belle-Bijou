from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Produto, Categoria

# Create your views here.
class Home(ListView):
    model = Produto
    template_name = "products/home.html"
    context_object_name = "produtos"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        categorias = Categoria.objects.all()
        contexto['categorias'] = categorias
        return contexto

class DetailProduto(DetailView):
    model = Produto
    template_name = "products/detalhe_produto.html"
    context_object_name = "produto"

def teste_carrinho(request):
    return render(request, "products/teste_carrinho.html")