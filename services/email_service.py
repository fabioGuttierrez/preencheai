import logging
from django.conf import settings
from django.core.mail import send_mail


def enviar_email(destinatario: str, assunto: str, mensagem: str) -> None:
    try:
        send_mail(
            subject=assunto,
            message=mensagem,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=[destinatario],
            fail_silently=False,
        )
    except Exception as exc:
        logging.getLogger(__name__).warning("Falha ao enviar email: %s", exc)
