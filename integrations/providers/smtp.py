import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from integrations.base import BaseIntegration

# Initialize the logger
log = logging.getLogger(__name__)


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
        }

    def validate_config(self):
        required = ["host", "port", "from_email", "to_email"]
        return all(key in self.config for key in required)

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

        # Build the email
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"New Subscriber: {subscriber.email}"
        msg["From"] = from_email
        msg["To"] = to_email

        # Plain-text body
        text_body = (
            f"New subscriber notification\n"
            f"---------------------------\n"
            f"Email:      {subscriber.email}\n"
            f"First Name: {subscriber.first_name or '—'}\n"
            f"Last Name:  {subscriber.last_name or '—'}\n"
            f"Phone:      {subscriber.phone or '—'}\n"
            f"Message:    {subscriber.message or '—'}\n"
            f"Audience:   {audience_name}\n"
            f"Source:     {source_domain}\n"
        )

        # HTML body
        html_body = f"""\
<html>
<body style="font-family: sans-serif; color: #333;">
  <h2>New Subscriber</h2>
  <table style="border-collapse: collapse;">
    <tr><td style="padding: 4px 12px; font-weight: bold;">Email</td><td>{subscriber.email}</td></tr>
    <tr><td style="padding: 4px 12px; font-weight: bold;">First Name</td><td>{subscriber.first_name or '—'}</td></tr>
    <tr><td style="padding: 4px 12px; font-weight: bold;">Last Name</td><td>{subscriber.last_name or '—'}</td></tr>
    <tr><td style="padding: 4px 12px; font-weight: bold;">Phone</td><td>{subscriber.phone or '—'}</td></tr>
    <tr><td style="padding: 4px 12px; font-weight: bold;">Message</td><td>{subscriber.message or '—'}</td></tr>
    <tr><td style="padding: 4px 12px; font-weight: bold;">Audience</td><td>{audience_name}</td></tr>
    <tr><td style="padding: 4px 12px; font-weight: bold;">Source</td><td>{source_domain}</td></tr>
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
