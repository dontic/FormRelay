import requests
import logging
from integrations.base import BaseIntegration

# Initialize the logger
log = logging.getLogger(__name__)

DEFAULT_NTFY_SERVER = "https://ntfy.sh"

SUPPORTED_LANGUAGES = ("en", "es")

TRANSLATIONS = {
    "en": {
        "title": "New Subscriber: {email}",
        "email": "Email",
        "first_name": "First Name",
        "last_name": "Last Name",
        "phone": "Phone",
        "message": "Message",
        "audience": "Audience",
        "source": "Source",
    },
    "es": {
        "title": "Nuevo Suscriptor: {email}",
        "email": "Correo",
        "first_name": "Nombre",
        "last_name": "Apellido",
        "phone": "Teléfono",
        "message": "Mensaje",
        "audience": "Audiencia",
        "source": "Origen",
    },
}


class NtfyIntegration(BaseIntegration):
    """ntfy.sh push-notification integration — sends a notification when a new subscriber is added."""

    @classmethod
    def config_schema(cls):
        return {
            "topic": "your-ntfy-topic",
            "server_url": "https://ntfy.sh",
            "access_token": "",
            "language": "en",
            "title": "",
        }

    def validate_config(self):
        required = ["topic"]
        return all(key in self.config for key in required)

    def _get_translations(self):
        lang = self.config.get("language", "en")
        if lang not in SUPPORTED_LANGUAGES:
            log.warning(f"Unsupported language '{lang}', falling back to English")
            lang = "en"
        return TRANSLATIONS[lang]

    def execute(self, subscriber, audience_settings=None):
        log.info(f"Executing ntfy notification for subscriber: {subscriber.email}")

        if not self.validate_config():
            log.error("Invalid ntfy configuration")
            raise ValueError("Invalid ntfy configuration")

        server_url = self.config.get("server_url", DEFAULT_NTFY_SERVER).rstrip("/")
        topic = self.config["topic"]
        access_token = self.config.get("access_token")

        # Allow audience-level overrides
        if audience_settings:
            topic = audience_settings.get("topic", topic)

        url = f"{server_url}/{topic}"

        audience_name = subscriber.audience.name if subscriber.audience else "Unknown"
        source_domain = subscriber.source.domain if subscriber.source else "N/A"

        t = self._get_translations()

        custom_title = self.config.get("title")
        title = (
            custom_title.format(email=subscriber.email)
            if custom_title
            else t["title"].format(email=subscriber.email)
        )
        message = (
            f"{t['email']}:      {subscriber.email}\n"
            f"{t['first_name']}: {subscriber.first_name or '—'}\n"
            f"{t['last_name']}:  {subscriber.last_name or '—'}\n"
            f"{t['phone']}:      {subscriber.phone or '—'}\n"
            f"{t['message']}:    {subscriber.message or '—'}\n"
            f"{t['audience']}:   {audience_name}\n"
            f"{t['source']}:     {source_domain}"
        )

        headers = {
            "Title": title,
            "Tags": "incoming_envelope",
        }

        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        log.debug(f"Sending ntfy notification to {url}")

        response = requests.post(url, data=message.encode("utf-8"), headers=headers)
        response.raise_for_status()

        result = response.json()
        log.debug(f"ntfy response: {result}")
        log.info(f"ntfy notification sent to topic '{topic}'")

        return {"success": True, "topic": topic, "id": result.get("id")}
