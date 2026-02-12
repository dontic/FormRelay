from integrations.providers.loops import LoopsIntegration
from integrations.providers.smtp import SMTPIntegration

# ... import others


class IntegrationRegistry:
    """Registry for all available integrations"""

    _integrations = {
        "loops": LoopsIntegration,
        "smtp": SMTPIntegration,
        # Add more here
    }

    @classmethod
    def get_integration(cls, integration_type, config):
        integration_class = cls._integrations.get(integration_type)
        if not integration_class:
            raise ValueError(f"Unknown integration type: {integration_type}")
        return integration_class(config)

    @classmethod
    def register(cls, name, integration_class):
        """Allow dynamic registration of custom integrations"""
        cls._integrations[name] = integration_class

    @classmethod
    def list_integrations(cls):
        return list(cls._integrations.keys())

    @classmethod
    def get_config_schema(cls, integration_type):
        """Return the config schema template for a given integration type."""
        integration_class = cls._integrations.get(integration_type)
        if not integration_class:
            return {}
        return integration_class.config_schema()
