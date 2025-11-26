from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, UpdateView, ListView, DetailView, View, TemplateView
from .models import CustomUser
from orders.models import Pedido
from .forms import RegisterForm, LoginForm
from django.urls import reverse_lazy, reverse
from .forms import RegisterForm, LoginForm, ProfileForm, CompleteSignupForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.http import Http404, HttpResponse
from .tokens import email_verification_token
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings


class RegisterView(CreateView):
    model = CustomUser # model respectivo
    form_class = RegisterForm # Formulário que será renderizado
    template_name = "accounts/cadastro.html" # Template que será renderizado
    success_url = reverse_lazy("login") # Caso o registro dê certo ele redireciona para a tela de login
    
class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_invalid(self, form):
        print("FORM INVÁLIDO ============")
        print(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        user = form.get_user()

        if not user.verificado: # caso o usuário não esteja verificado
            self.request.session["verificar_email_usuario_id"] = user.id # salva o id do usuário na sessão

            messages.error(self.request, "Você precisa verificar seu e-mail antes de logar.")
            return redirect("enviar-verificacao")

        return super().form_valid(form)
    
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

# -=-=-=-=-=-=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-=-=-=-=-=--=- Confirmar Conta -=-=-=-=-=-=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-=-=-=-=-=--=-

class ConfirmarEmailEnviado(TemplateView): # view que renderiza a tela de email enviado
    template_name='accounts/verificar_enviado.html'

class EnviarEmailVerificacaoView(View): # view que envia o email
    def get(self, request, *args, **kwargs): # função que é chamada pela requisição GET
        user_id = request.session.get("verificar_email_usuario_id") # pega o id do usuario armazenado na sessão

        if not user_id: # caso não encontre o id volta para a tela de login
            return redirect("login")

        user = CustomUser.objects.get(pk=user_id) # pega o usuário no banco de dados

        if user.verificado: # caso o usuário já esteja verificado é levado para a tela inicial
            return redirect("home")

        self.enviar_email(request, user) # roda a função de enviar o email

        try: # deleta o campo com o id do usuário da sessão
            del request.session["verificar_email_usuario_id"]
        except KeyError:
            pass

        return redirect("verificacao-enviada") # redireciona para a tela de email enviado
    
    def enviar_email(self, request, user): # função que envia o email
        current_site = get_current_site(request) # pega a url do site
        token = email_verification_token.make_token(user) # cria um token para o link
        uid = user.pk # salva o id do usuário (chave primária)

        link = request.build_absolute_uri( # cria o link
            reverse('verificar-email', kwargs={'uid': uid, 'token': token})
        )

        assunto = "Verifique sua conta" # monta assunto do email
        mensagem = render_to_string("accounts/verificar_email.html", { # monta a mensagem do email com o template
            "user": user,
            "link": link,
        })

        email = EmailMultiAlternatives(assunto, mensagem, f'{settings.DEFAULT_FROM_EMAIL}', [user.email]) # engloba tudo para enviar o email
        email.attach_alternative(mensagem, "text/html") # padroniza o email como text/html
        email.send() # manda o email

class VerificarEmailView(TemplateView): # view que muda o campo de verificado
    template_name = "accounts/verificar_feito.html"

    def get(self, request, *args, **kwargs):
        uid = kwargs.get("uid") # pega o id do usuário passado pelo link
        token = kwargs.get("token") # pega o token passado pelo link

        try: # tenta encontrar o usuário no bd
            user = CustomUser.objects.get(pk=uid)
        except CustomUser.DoesNotExist:
            return HttpResponse("Usuário inválido.")

        if user.verificado: # caso o usuário já esteja verificado nada muda
            return super().get(request, *args, **kwargs)

        if email_verification_token.check_token(user, token): # caso o token seja válido
            user.verificado = True # verifica o usuário
            user.save() # salva no banco
            return super().get(request, *args, **kwargs)

        return HttpResponse("Link inválido ou expirado.") # em qualquer outro caso exibe essa mensagem