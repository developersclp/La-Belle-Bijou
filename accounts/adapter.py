from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        extra_data = sociallogin.account.extra_data

        email = extra_data.get("email")
        name = extra_data.get("name")
        print(name)

        if not name:
            nome = extra_data.get("given_name", "")
            sobrenome = extra_data.get("family_name", "")
        else:
            partes_nome = name.split(" ", 1)
            nome = partes_nome[0]
            if len(partes_nome) > 1:
                sobrenome = partes_nome[1]
            else:
                sobrenome = ""

        # Garante que o email, nome e sobrenome sejam preenchidos antes do save
        if email and not user.email:
            user.email = email

        if nome and not user.first_name:
            user.first_name = nome

        if sobrenome and not user.last_name:
            user.last_name = sobrenome

        return user
