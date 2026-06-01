"""Lightweight, fail-safe email helper.

If SMTP_HOST is not configured, emails are logged instead of sent, so the
app works out-of-the-box in development without an SMTP server. Sending
never raises into the request path - failures are logged and swallowed.
"""
import logging
import smtplib
from email.message import EmailMessage

from config import settings

logger = logging.getLogger("aquaterra.mailer")


def send_email(to: str, subject: str, body: str, html: str | None = None) -> bool:
    """Send an email. Returns True if sent, False if skipped/failed."""
    if not to:
        return False
    if not settings.SMTP_HOST:
        logger.info("[MAIL skipped - no SMTP] to=%s subject=%s", to, subject)
        return False
    try:
        msg = EmailMessage()
        msg["From"] = settings.MAIL_FROM
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        if html:
            msg.add_alternative(html, subtype="html")

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        logger.info("[MAIL sent] to=%s subject=%s", to, subject)
        return True
    except Exception as e:  # never break the request because of email
        logger.warning("[MAIL failed] to=%s subject=%s error=%s", to, subject, e)
        return False


def send_order_confirmation(order) -> None:
    items = "\n".join(f"  - {i['name']} x{i['qty']}" for i in (order.items_snapshot or []))
    body = (
        f"Hola {order.buyer_name or ''},\n\n"
        f"Tu pago fue confirmado. Gracias por tu compra en Aqua-Terra.\n\n"
        f"Orden: {order.buy_order}\n"
        f"Total: {order.currency} {order.total:,.0f}\n"
        f"Autorizacion: {order.webpay_authorization_code}\n\n"
        f"Productos:\n{items}\n\n"
        f"Te contactaremos para coordinar el envio.\n\nAqua-Terra"
    )
    send_email(order.buyer_email, f"Confirmacion de compra {order.buy_order}", body)


def send_contact_notification(submission) -> None:
    admin_to = settings.MAIL_ADMIN or settings.CONTACT_EMAIL
    body = (
        f"Nuevo contacto recibido:\n\n"
        f"Nombre: {submission.name}\n"
        f"Email: {submission.email}\n"
        f"Telefono: {submission.phone}\n"
        f"Tipo: {submission.inquiry_type}\n"
        f"Pilar: {submission.pillar}\n\n"
        f"Mensaje:\n{submission.message}\n"
    )
    send_email(admin_to, f"[Contacto] {submission.name}", body)
