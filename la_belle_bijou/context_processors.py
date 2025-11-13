from products.models import Categoria

def categorias(request):
    try:
        categorias = Categoria.objects.all()
        return {'categorias': categorias}
    except:
        return{'categorias': []}