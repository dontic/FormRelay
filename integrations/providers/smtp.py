import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from integrations.base import BaseIntegration

# Initialize the logger
log = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = ("en", "es")

TRANSLATIONS = {
    "en": {
        "subject": "New Subscriber: {email}",
        "heading": "New Subscriber",
        "notification": "New subscriber notification",
        "email": "Email",
        "first_name": "First Name",
        "last_name": "Last Name",
        "phone": "Phone",
        "message": "Message",
        "audience": "Audience",
        "source": "Source",
    },
    "es": {
        "subject": "Nuevo Suscriptor: {email}",
        "heading": "Nuevo Suscriptor",
        "notification": "Notificación de nuevo suscriptor",
        "email": "Correo",
        "first_name": "Nombre",
        "last_name": "Apellido",
        "phone": "Teléfono",
        "message": "Mensaje",
        "audience": "Audiencia",
        "source": "Origen",
    },
}


class SMTPIntegration(BaseIntegration):
    """SMTP email notification integration — sends an email when a new subscriber is added."""

    @classmethod
    def config_schema(cls):
        return {
            "host": "smtp.example.com",
            "port": 587,
            "username": "your-smtp-username",
            "password": "your-smtp-password",
            "use_tls": True,
            "from_email": "notifications@example.com",
            "to_email": "admin@example.com",
            "language": "en",
        }

    def validate_config(self):
        required = ["host", "port", "from_email", "to_email"]
        return all(key in self.config for key in required)

    def _get_translations(self):
        lang = self.config.get("language", "en")
        if lang not in SUPPORTED_LANGUAGES:
            log.warning(f"Unsupported language '{lang}', falling back to English")
            lang = "en"
        return TRANSLATIONS[lang]

    def execute(self, subscriber, audience_settings=None):
        log.info(f"Executing SMTP notification for subscriber: {subscriber.email}")

        if not self.validate_config():
            log.error("Invalid SMTP configuration")
            raise ValueError("Invalid SMTP configuration")

        host = self.config["host"]
        port = int(self.config.get("port", 587))
        username = self.config.get("username")
        password = self.config.get("password")
        use_tls = self.config.get("use_tls", True)
        from_email = self.config["from_email"]
        to_email = self.config["to_email"]

        # Allow audience-level overrides
        if audience_settings:
            to_email = audience_settings.get("to_email", to_email)

        audience_name = subscriber.audience.name if subscriber.audience else "Unknown"
        source_domain = subscriber.source.domain if subscriber.source else "N/A"

        t = self._get_translations()

        # Build the email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = t["subject"].format(email=subscriber.email)
        msg["From"] = from_email
        msg["To"] = to_email

        # Plain-text body
        text_body = (
            f"{t['notification']}\n"
            f"---------------------------\n"
            f"{t['email']}:      {subscriber.email}\n"
            f"{t['first_name']}: {subscriber.first_name or '—'}\n"
            f"{t['last_name']}:  {subscriber.last_name or '—'}\n"
            f"{t['phone']}:      {subscriber.phone or '—'}\n"
            f"{t['message']}:    {subscriber.message or '—'}\n"
            f"{t['audience']}:   {audience_name}\n"
            f"{t['source']}:     {source_domain}\n"
        )

        # HTML body
        html_body = f"""\
<html>
<body style="font-family: sans-serif; color: #333;">
  <h2>{t['heading']}</h2>
  <table style="border-collapse: collapse;">
    <tr><td style="padding: 4px 12px; font-weight: bold;">{t['email']}</td><td>{subscriber.email}</td></tr>
    <tr><td style="padding: 4px 12px; font-weight: bold;">{t['first_name']}</td><td>{subscriber.first_name or '—'}</td></tr>
    <tr><td style="padding: 4px 12px; font-weight: bold;">{t['last_name']}</td><td>{subscriber.last_name or '—'}</td></tr>
    <tr><td style="padding: 4px 12px; font-weight: bold;">{t['phone']}</td><td>{subscriber.phone or '—'}</td></tr>
    <tr><td style="padding: 4px 12px; font-weight: bold;">{t['message']}</td><td>{subscriber.message or '—'}</td></tr>
    <tr><td style="padding: 4px 12px; font-weight: bold;">{t['audience']}</td><td>{audience_name}</td></tr>
    <tr><td style="padding: 4px 12px; font-weight: bold;">{t['source']}</td><td>{source_domain}</td></tr>
  </table>
</body>
</html>"""

        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        log.debug(f"Sending SMTP notification to {to_email} via {host}:{port}")

        try:
            with smtplib.SMTP(host, port) as server:
                if use_tls:
                    server.starttls()
                if username and password:
                    server.login(username, password)
                server.sendmail(from_email, [to_email], msg.as_string())
        except smtplib.SMTPException as exc:
            log.error(f"SMTP error: {exc}")
            raise ValueError(f"SMTP error: {exc}") from exc

        log.info(f"SMTP notification sent to {to_email}")
        return {"success": True, "to_email": to_email}
