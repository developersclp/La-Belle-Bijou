from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        extra_data = sociallogin.account.extra_data
        email = extra_data.get("email")

        # Garante que o email seja preenchido antes do save
        if email and not user.email:
            user.email = email

        return user
