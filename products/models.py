from django.db import models
from accounts.models import CustomUser

# Create your models here.
class Categoria(models.Model):
    nome = models.CharField(max_length=50)

    def __str__(self):
        return self.nome

class ProdutoManager(models.Manager):
    def mais_vendidos(self, limite=10):
        """
        Retorna os produtos mais vendidos (com mais saídas por VENDA)
        """
        from django.db.models import Sum, Q
        
        return self.annotate(
            total_vendas=Sum(
                'movimentacoes__quantidade',
                filter=Q(movimentacoes__tipo='SAIDA', movimentacoes__motivo='VENDA')
            )
        ).filter(
            total_vendas__isnull=False,
            total_vendas__gt=0
        ).order_by('-total_vendas')[:limite]

class Produto(models.Model):
    nome = models.CharField(max_length=50)
    descricao = models.TextField(null=True, blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    categorias = models.ManyToManyField(Categoria, related_name="produtos")
    imagem_principal = models.ImageField(upload_to="produtos/principal/", null=True, blank=True)
    is_active = models.BooleanField(default=True)

    objects = ProdutoManager()

    @property
    def estoque_atual(self): # função para calcular o estoque atual de cada produto
        entradas = self.movimentacoes.filter(tipo="ENTRADA").aggregate(total=models.Sum("quantidade"))["total"] or 0
        saidas = self.movimentacoes.filter(tipo="SAIDA").aggregate(total=models.Sum("quantidade"))["total"] or 0
        return entradas - saidas

    def __str__(self):
        return f'{self.nome}: {self.descricao}'
    
class ImagemProduto(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="imagens")
    imagem = models.ImageField(upload_to="produtos/galeria/")

    def __str__(self):
        return f"Imagem de {self.produto.nome}"
    
class MovimentacaoEstoque(models.Model):
    TIPOS = (
        ("ENTRADA", "Entrada"),
        ("SAIDA", "Saída"),
    )

    MOTIVOS = [
        ("COMPRA", "Compra de fornecedor"),
        ("VENDA", "Venda para cliente"),
    ]

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name="movimentacoes")
    tipo = models.CharField(max_length=10, choices=TIPOS)
    quantidade = models.PositiveIntegerField()
    motivo = models.CharField(max_length=255, choices=MOTIVOS)
    data = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.tipo} - {self.produto.nome} ({self.quantidade})"