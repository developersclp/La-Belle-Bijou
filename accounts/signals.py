from allauth.socialaccount.signals import social_account_added, social_account_updated
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from allauth.account.signals import user_logged_in

User = get_user_model()

@receiver([social_account_added, social_account_updated])
def fill_user_data(request, sociallogin, **kwargs):
    user = sociallogin.user
    data = sociallogin.account.extra_data

    if sociallogin.account.provider == "google":
        email = data.get("email")
        first_name = data.get("given_name")
        last_name = data.get("family_name")

        # Preenche se estiver vazio
        if not user.email:
            user.email = email
        if not user.first_name:
            user.first_name = first_name
        if not user.last_name:
            user.last_name = last_name

        user.save()

@receiver(user_logged_in)
def redirect_to_complete_signup(request, user, **kwargs):
    """
    Se o usuário logar (por Google ou outro método) e ainda não tiver CPF ou telefone,
    salva um flag na sessão para forçar o redirecionamento.
    """
    if not user.cpf or not user.telefone:
        request.session['needs_profile_completion'] = True