import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class SendGridEmailBackend(BaseEmailBackend):
    """
    Backend de email para Django usando SendGrid Web API v3 (HTTPS).
    Con esto, cualquier send_mail() (password reset, confirmaciones, etc.) funciona en Railway.

    Variables requeridas:
      - SENDGRID_API_KEY
      - SENDGRID_FROM_EMAIL (remitente verificado en SendGrid)
    """

    def send_messages(self, email_messages):
        api_key = getattr(settings, "SENDGRID_API_KEY", "").strip()
        from_email = (
            getattr(settings, "SENDGRID_FROM_EMAIL", "").strip()
            or getattr(settings, "DEFAULT_FROM_EMAIL", "").strip()
        )

        if not api_key or not from_email:
            if self.fail_silently:
                return 0
            raise RuntimeError("SendGrid no configurado: falta SENDGRID_API_KEY o SENDGRID_FROM_EMAIL/DEFAULT_FROM_EMAIL")

        sent_count = 0
        timeout = int(getattr(settings, "EMAIL_TIMEOUT", 20))

        for message in email_messages:
            to_emails = list(message.to or [])
            if not to_emails:
                continue

            subject = message.subject or ""
            body_text = message.body or ""

            # Si trae HTML en alternatives, lo mandamos también
            html_body = None
            if hasattr(message, "alternatives"):
                for alt_content, alt_mimetype in message.alternatives:
                    if alt_mimetype == "text/html":
                        html_body = alt_content
                        break

            payload = {
                "personalizations": [{"to": [{"email": e} for e in to_emails]}],
                "from": {"email": from_email, "name": "Brujitas"},
                "subject": subject,
                "content": [{"type": "text/plain", "value": body_text}],
            }

            if html_body:
                payload["content"].append({"type": "text/html", "value": html_body})

            resp = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=timeout,
            )

            if 200 <= resp.status_code < 300:
                sent_count += 1
            else:
                # Para que no quede silencioso y puedas ver la causa real en logs
                if not self.fail_silently:
                    raise RuntimeError(f"SendGrid error {resp.status_code}: {resp.text[:500]}")

        return sent_count
