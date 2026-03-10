import hashlib
import requests
import logging
from integrations.base import BaseIntegration

# Initialize the logger
log = logging.getLogger(__name__)


class MailchimpIntegration(BaseIntegration):
    """Mailchimp integration"""

    @classmethod
    def config_schema(cls):
        return {
            "api_key": "your-mailchimp-api-key",
            "list_id": "your-mailchimp-audience-id",
            "server_prefix": "us6",
        }

    def validate_config(self):
        required = ["api_key", "list_id", "server_prefix"]
        return all(key in self.config for key in required)

    def _get_base_url(self):
        return f"https://{self.config['server_prefix']}.api.mailchimp.com/3.0"

    def _get_auth(self):
        return ("anystring", self.config["api_key"])

    def _subscriber_hash(self, email):
        return hashlib.md5(email.lower().encode()).hexdigest()

    def execute(self, subscriber, audience_settings=None):
        log.info(f"Executing Mailchimp integration for subscriber: {subscriber.email}")

        if not self.validate_config():
            log.error("Invalid Mailchimp configuration")
            raise ValueError("Invalid Mailchimp configuration")

        list_id = self.config["list_id"]
        base_url = self._get_base_url()
        auth = self._get_auth()

        merge_fields = {
            "FNAME": subscriber.first_name or "",
            "LNAME": subscriber.last_name or "",
        }
        if subscriber.phone:
            merge_fields["PHONE"] = subscriber.phone

        data = {
            "email_address": subscriber.email,
            "status": "subscribed",
            "merge_fields": merge_fields,
        }

        log.debug(f"Mailchimp member data to send: {data}")

        url = f"{base_url}/lists/{list_id}/members"
        response = requests.post(url, json=data, auth=auth)
        result = response.json()
        log.debug(f"Mailchimp response: {result}")

        if response.status_code not in (200, 400):
            response.raise_for_status()

        # 400 with title "Member Exists" is acceptable (already subscribed)
        if response.status_code == 400 and result.get("title") != "Member Exists":
            raise ValueError(f"Mailchimp API error: {result.get('detail', result.get('title', 'Unknown error'))}")

        # Apply tags from subscriber's custom_data if present
        tags = (subscriber.custom_data or {}).get("tags", [])
        if tags:
            log.debug(f"Adding Mailchimp tags: {tags}")
            subscriber_hash = self._subscriber_hash(subscriber.email)
            tags_url = f"{base_url}/lists/{list_id}/members/{subscriber_hash}/tags"
            tags_payload = {
                "tags": [{"name": tag, "status": "active"} for tag in tags]
            }
            tags_response = requests.post(tags_url, json=tags_payload, auth=auth)
            log.debug(f"Mailchimp tags response status: {tags_response.status_code}")
            if tags_response.status_code != 204:
                tags_result = tags_response.json()
                raise ValueError(f"Mailchimp tags error: {tags_result.get('detail', tags_result.get('title', 'Unknown error'))}")

        return result
