import requests
import logging
from integrations.base import BaseIntegration

# Initialize the logger
log = logging.getLogger(__name__)

DEFAULT_NTFY_SERVER = "https://ntfy.sh"


class NtfyIntegration(BaseIntegration):
    """ntfy.sh push-notification integration — sends a notification when a new subscriber is added."""

    @classmethod
    def config_schema(cls):
        return {
            "topic": "your-ntfy-topic",
            "server_url": "https://ntfy.sh",
            "access_token": "",
        }

    def validate_config(self):
        required = ["topic"]
        return all(key in self.config for key in required)

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

        title = f"New Subscriber: {subscriber.email}"
        message = (
            f"Email:      {subscriber.email}\n"
            f"First Name: {subscriber.first_name or '—'}\n"
            f"Last Name:  {subscriber.last_name or '—'}\n"
            f"Phone:      {subscriber.phone or '—'}\n"
            f"Message:    {subscriber.message or '—'}\n"
            f"Audience:   {audience_name}\n"
            f"Source:     {source_domain}"
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
