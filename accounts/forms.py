from django import forms
from .models import CustomUser, Endereco
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from .validators import RegisterValidator

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Senha"}), label='Senha') # define o campo de senha
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Confirme a senha"}), label="Confirme a senha") # define o campo de confirmação de senha
    cpf = forms.CharField(
        max_length=14,
        widget=forms.TextInput(attrs={
            "placeholder": "CPF",
            "inputmode": "numeric",
        })
    )
    telefone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            "placeholder": "Telefone",
            "inputmode": "tel",
        })
    )

    class Meta:
        model = CustomUser # define que esse formulário irá criar/editar instâncias da tabela CustomUser
        fields = ["username", "cpf", "email", "telefone", "password"] # define a ordem e os campos que irão aparecer
        labels = { # define os labels de cada campo
            "username": "Usuário",
            "cpf": "CPF",
            "email": "E-mail",
            "telefone": "Telefone",
        }
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Nome de usuário"}),
            "email": forms.EmailInput(attrs={"placeholder": "E-mail"}),
            "telefone": forms.TextInput(attrs={
                "placeholder": "Telefone",
                "inputmode": "tel", # Teclado numérico com símbolos em mobile
            }),
        }
        help_texts = { # define os textos de apoio para cada campo
            "username": None,
        }
    
    validator = RegisterValidator()

    def clean_cpf(self):
        return self.validator.validate_cpf(self.cleaned_data.get("cpf"))

    def clean_telefone(self):
        return self.validator.validate_phone(self.cleaned_data.get("telefone"))
        
    def clean(self): # função que serve para fazer validações personalizadas antes de salvar o objeto
        cleaned_data = super().clean() # retorna um dicionário com os valores já validados dos campos do formulário
        password = cleaned_data.get("password") # pega o campo de senha do dicionário
        password_confirm = cleaned_data.get("password_confirm") # pega o campo de confimação de senha do dicionário

        if password and password_confirm and password != password_confirm: # verifica se as senhas são diferentes
            self.add_error("password_confirm", "As senhas não coincidem!") # caso forem diferentes retorna o erro
        else:
            try:
                validate_password(password)
            except ValidationError as e:
                self.add_error("password_confirm", e)

        return cleaned_data # retorna o dicionário para que o django tenha os campos validados
    
    def save(self, commit=True): # sobrescreve o método save padrão para então ser customizado
        user = super().save(commit=False) # cria a instância CustomUser sem salvar no banco
        user.set_password(self.cleaned_data["password"])  # encripta a senha
        if commit:
            user.save() # salva no banco
        return user # retorna o usuário que acaba de ser criado


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autofocus": True})
    )

    error_messages = {
        'invalid_login': (
            "E-mail ou senha incorretos. Verifique e tente novamente."
        ),
        'inactive': ("Esta conta está inativa."),
    }

# Novo formulário para edição de perfil
class ProfileForm(forms.ModelForm):
    # Campos do usuário
    telefone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            "placeholder": "Telefone",
            "inputmode": "tel",
        })
    )
    cpf = forms.CharField(
        max_length=14,
        widget=forms.TextInput(attrs={
            "placeholder": "CPF",
            "inputmode": "numeric",
        })
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'telefone', 'data_nasc', 'cpf']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'data_nasc': 'Data de nascimento',
        }

    validator = RegisterValidator()

    def clean_cpf(self):
        return self.validator.validate_cpf(self.cleaned_data.get("cpf"))

    def clean_telefone(self):
        return self.validator.validate_phone(self.cleaned_data.get("telefone"))


class CompleteSignupForm(forms.ModelForm):
    telefone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            "placeholder": "Telefone",
            "inputmode": "tel",
        })
    )
    cpf = forms.CharField(
        max_length=14,
        widget=forms.TextInput(attrs={
            "placeholder": "CPF",
            "inputmode": "numeric",
        })
    )
    class Meta:
        model = CustomUser
        fields = ['telefone', 'cpf']

    validator = RegisterValidator()

    def clean_cpf(self):
        return self.validator.validate_cpf(self.cleaned_data.get("cpf"))

    def clean_telefone(self):
        return self.validator.validate_phone(self.cleaned_data.get("telefone"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['telefone'].required = True
        self.fields['cpf'].required = True

class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = ["rua", "numero", "complemento", "cep"]
        widgets = {
            "rua": forms.TextInput(attrs={"placeholder": "Rua", "class": "form-control"}),
            "numero": forms.TextInput(attrs={"placeholder": "Número", "class": "form-control"}),
            "complemento": forms.TextInput(attrs={"placeholder": "Complemento (opcional)", "class": "form-control"}),
            "cep": forms.TextInput(attrs={"placeholder": "CEP", "class": "form-control"}),
        }