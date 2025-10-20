from django.core.mail.backends.base import BaseEmailBackend
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os

class SendGridBackend(BaseEmailBackend):
    """
    Backend de envio de e-mails via API HTTP da SendGrid.
    Substitui o uso de SMTP (porta 587) e evita erros de rede.
    """
    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        sg = SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
        sent_count = 0

        for message in email_messages:
            try:
                mail = Mail(
                    from_email=message.from_email,
                    to_emails=message.to,
                    subject=message.subject,
                    html_content=message.body,
                )
                sg.send(mail)
                sent_count += 1
            except Exception as e:
                print(f"❌ Falha ao enviar e-mail: {e}")

        return sent_count
