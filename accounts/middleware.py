from django.shortcuts import redirect
from django.urls import reverse

class CompleteProfileMiddleware:
    """
    Redireciona o usuário para a tela de completar cadastro se ele ainda não
    tiver preenchido CPF e telefone. Bloqueia acesso a qualquer outra página.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        # Caminhos que o usuário pode acessar sem restrição
        allowed_paths = [
            reverse('completar-cadastro'),
            reverse('logout'),  # permite deslogar
        ]

        if user.is_authenticated:
            # Se faltar dados obrigatórios
            if (not user.cpf or not user.telefone or not user.first_name or not user.last_name):
                # E não estiver já na tela de completar cadastro
                if not any(request.path.startswith(p) for p in allowed_paths):
                    return redirect(reverse('completar-cadastro'))

        return self.get_response(request)
