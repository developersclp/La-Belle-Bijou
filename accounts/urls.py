from django.urls import path
from .views import *

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),  # Nova URL para edição de perfil
    path("completar-cadastro/", complete_signup, name="completar-cadastro"),
    path("ver-pedidos/", VerPedidos.as_view(), name="ver-pedidos"),
    path("pedido/<int:pk>/", PedidoDetalheView.as_view(), name="detalhe-pedido"),

    # -=-=-=-=-=-=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-=-=-=-=-=--=- Reset de Senha -=-=-=-=-=-=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-=-=-=-=-=--=-

    path('reset-senha/', ResetPasswordView.as_view(), name='reset-senha'),
    path('reset-senha/enviado/', ResetPasswordDoneView.as_view(), name='reset-senha-enviado'),
    path('reset/<uidb64>/<token>/', ResetPasswordConfirmView.as_view(), name='reset-senha-confirm'),
    path('reset-senha/concluido/', ResetPasswordCompleteView.as_view(), name='reset-concluido'),

    path("enviar-verificacao/", EnviarEmailVerificacaoView.as_view(), name="enviar-verificacao"),
    path("verificacao-enviada/", ConfirmarEmailEnviado.as_view(), name="verificacao-enviada"),
    path("verificar/<int:uid>/<str:token>/", VerificarEmailView.as_view(), name="verificar-email"),
]