from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from .models import CustomUser
from orders.models import Pedido, ItemPedido
from .forms import RegisterForm, LoginForm
from django.urls import reverse_lazy
from .forms import RegisterForm, LoginForm, ProfileForm, CompleteSignupForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.http import Http404

class RegisterView(CreateView):
    model = CustomUser # model respectivo
    form_class = RegisterForm # Formulário que será renderizado
    template_name = "accounts/cadastro.html" # Template que será renderizado
    success_url = reverse_lazy("login") # Caso o registro dê certo ele redireciona para a tela de login
    
class LoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:  # se for admin
            return reverse_lazy("produtos-adm")  # manda para dashboard admin
        return reverse_lazy("home")  # manda para home normal

class LogoutView(LogoutView):
    next_page = "login"

# Nova View para edição de perfil
class ProfileView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileForm
    template_name = "accounts/editar_perfil.html"
    success_url = reverse_lazy("profile")
    
    def get_object(self):
        return self.request.user
    
@login_required
def complete_signup(request):
    user = request.user

    if user.telefone and user.cpf:
        return redirect('home')

    if request.method == 'POST':
        form = CompleteSignupForm(request.POST, instance=user)
        if form.is_valid(): 
            form.save()
            return redirect('home')
    else:
        form = CompleteSignupForm(instance=user)

    return render(request, 'accounts/complete_signup.html', {'form': form})

class VerPedidos(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'accounts/pedidos.html'
    context_object_name = 'pedidos'

    def get_queryset(self):
        user = self.request.user
        return Pedido.objects.filter(usuario=user).order_by('-data_criacao')

class PedidoDetalheView(LoginRequiredMixin, DetailView):
    model = Pedido
    template_name = 'accounts/ver_pedido.html'
    context_object_name = 'pedido'

    def get_object(self, queryset=None):
        pedido = super().get_object(queryset)

        if pedido.usuario != self.request.user:
            raise Http404("Pedido não encontrado")
        return pedido
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pedido = self.get_object()
        context["itens_pedido"] = pedido.itens.all()

        return context

# -=-=-=-=-=-=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-=-=-=-=-=--=- Reset de Senha -=-=-=-=-=-=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-=-=-=-=-=--=-

class ResetPasswordView(auth_views.PasswordResetView): # view que manda o email
    template_name = 'accounts/reset_password.html'
    email_template_name = 'accounts/reset_password_email.html'
    html_email_template_name = 'accounts/reset_password_email.html'
    subject_template_name = 'accounts/reset_password_assunto.txt'
    success_url = reverse_lazy('reset-senha-enviado')

class ResetPasswordDoneView(auth_views.PasswordResetDoneView): # view que renderiza a tela de email enviado
    template_name = 'accounts/reset_password_enviado.html'

class ResetPasswordConfirmView(auth_views.PasswordResetConfirmView): # view que renderiza o formulário de reset de senha
    template_name = 'accounts/reset_password_form.html'
    success_url = reverse_lazy('reset-concluido')

class ResetPasswordCompleteView(auth_views.PasswordResetCompleteView): # view que renderiza a tela de confirmação de senha alterada
    template_name = 'accounts/reset_password_feito.html'