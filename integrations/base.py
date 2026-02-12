from abc import ABC, abstractmethod


class BaseIntegration(ABC):
    """Base class for all integrations"""

    def __init__(self, config):
        self.config = config

    @classmethod
    def config_schema(cls):
        """
        Return a dict template showing the expected config keys and placeholder values.
        Subclasses should override this to document their required/optional config fields.
        """
        return {}

    @abstractmethod
    def execute(self, subscriber, audience_settings=None):
        """Execute the integration for a subscriber"""
        pass

    @abstractmethod
    def validate_config(self):
        """Validate the integration configuration"""
        pass

    def get_name(self):
        return self.__class__.__name__
