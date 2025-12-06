from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.
# Manager que permite a remoção do campo username do CustomUser
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O email é obrigatório")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)
        
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    telefone = models.CharField(null=True, max_length=11)
    cpf = models.CharField(max_length=11, unique=True)
    data_nasc = models.DateField(null=True, blank=True)
    verificado = models.BooleanField(default=False)

    # Retirando username padrão do CustomUser já que o email é o identificador e a nomeação do usuário é com Nome e Sobrenome
    username = None
    objects = CustomUserManager()

    REQUIRED_FIELDS = ["cpf", "first_name", "last_name",]
    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email

class Endereco(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="enderecos")
    rua = models.CharField(max_length=255)
    bairro = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=255, blank=True, null=True)
    cep = models.CharField(max_length=9)
    cidade = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    
    def __str__(self):
        return f"{self.rua}, {self.numero} - {self.cep}"