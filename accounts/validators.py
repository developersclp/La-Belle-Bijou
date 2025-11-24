from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe
import re

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

class RegisterValidator:
    def clean_digits(self, value):
        return re.sub(r"\D", "", value or "")
    
    def validate_cpf(self, value):
        cpf = self.clean_digits(value)

        if not cpf:
            raise ValidationError("Informe um CPF.")

        if len(cpf) < 11:
            raise ValidationError("CPF incompleto.")

        if len(cpf) > 11:
            raise ValidationError("CPF deve ter apenas 11 dígitos.")

        if cpf in [s * 11 for s in "0123456789"]:
            raise ValidationError("CPF inválido.")

        return cpf
            
    
    def validate_phone(self, value):
        phone = self.clean_digits(value)

        if len(phone) < 11:
            raise ValidationError("Telefone incompleto")

        return phone
