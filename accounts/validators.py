from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe

class CustomPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(_("A senha deve ter pelo menos 8 caracteres."))

        if not any(c.isupper() for c in password):
            raise ValidationError(_("A senha deve conter pelo menos uma letra maiúscula."))

        if not any(c.isdigit() for c in password):
            raise ValidationError(_("A senha deve conter pelo menos um número."))

        if not any(c in "!@#$%^&*()-_=+[{]};:'\",<.>/?\\|" for c in password):
            raise ValidationError(_("A senha deve conter pelo menos um caractere especial."))

    def get_help_text(self):
        return mark_safe(
            """
                Regras:
                <li>Mínimo de 8 caracteres</li>
                <li>Pelo menos uma letra maiúscula</li>
                <li>Pelo menos um número</li>
                <li>Pelo menos um caractere especial</li>
            """
        )