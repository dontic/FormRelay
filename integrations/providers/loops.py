import requests
import logging
from integrations.base import BaseIntegration

# Initialize the logger
log = logging.getLogger(__name__)


class LoopsIntegration(BaseIntegration):
    """Loops.so integration"""

    @classmethod
    def config_schema(cls):
        return {
            "api_key": "your-loops-api-key",
        }

    def validate_config(self):
        required = ["api_key"]
        return all(key in self.config for key in required)

    def execute(self, subscriber, audience_settings=None):
        log.info(f"Executing Loops integration for subscriber: {subscriber.email}")

        if not self.validate_config():
            log.error("Invalid Loops configuration")
            raise ValueError("Invalid Loops configuration")

        url = "https://app.loops.so/api/v1/contacts/create"
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json",
        }

        data = {
            "email": subscriber.email,
            "firstName": subscriber.first_name,
            "lastName": subscriber.last_name,
            "source": subscriber.source.domain if subscriber.source else None,
        }

        log.debug(f"Loops data to send: {data}")

        # Merge custom data
        if audience_settings:
            data.update(audience_settings.get("custom_fields", {}))

        response = requests.post(url, json=data, headers=headers)
        result = response.json()
        log.debug(f"Loops response: {result}")
        response.raise_for_status()

        if not result.get("success", False):
            message = result.get("message", "Unknown error from Loops API")
            raise ValueError(f"Loops API error: {message}")

        return result
