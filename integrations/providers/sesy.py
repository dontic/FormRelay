import requests
import logging
from integrations.base import BaseIntegration

# Initialize the logger
log = logging.getLogger(__name__)


class SesyIntegration(BaseIntegration):
    """Sesy email campaign integration"""

    @classmethod
    def config_schema(cls):
        return {
            "api_key": "your-sesy-api-key",
            "project_pk": 1,
            "base_url": "https://your-sesy-instance.example.com",
        }

    def validate_config(self):
        required = ["api_key", "project_pk", "base_url"]
        return all(key in self.config for key in required)

    def execute(self, subscriber, audience_settings=None):
        log.info(f"Executing Sesy integration for subscriber: {subscriber.email}")

        if not self.validate_config():
            log.error("Invalid Sesy configuration")
            raise ValueError("Invalid Sesy configuration")

        base_url = self.config["base_url"].rstrip("/")
        url = f"{base_url}/api/sesy/public/members/"
        headers = {
            "X-API-Key": self.config["api_key"],
            "Content-Type": "application/json",
        }

        data = {
            "project_pk": self.config["project_pk"],
            "email": subscriber.email,
        }

        if subscriber.first_name:
            data["first_name"] = subscriber.first_name
        if subscriber.last_name:
            data["last_name"] = subscriber.last_name

        tags = (subscriber.custom_data or {}).get("tags", [])
        if audience_settings:
            tags = audience_settings.get("tags", tags)
        if tags:
            data["tags"] = tags

        log.debug(f"Sesy data to send: {data}")

        response = requests.post(url, json=data, headers=headers)
        log.debug(f"Sesy response status: {response.status_code}")
        response.raise_for_status()

        result = response.json() if response.content else {}
        return result
