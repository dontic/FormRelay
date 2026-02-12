from django.db import models
from integrations.registry import IntegrationRegistry


class Integration(models.Model):
    """
    Represents a configured integration provider (e.g. a Loops account with an API key).
    """

    INTEGRATION_TYPE_CHOICES = [
        (key, key.replace("_", " ").title())
        for key in IntegrationRegistry.list_integrations()
    ]

    name = models.CharField(
        max_length=255, help_text="Friendly name for this integration"
    )
    integration_type = models.CharField(
        max_length=50,
        choices=INTEGRATION_TYPE_CHOICES,
        help_text="The provider type (e.g. loops)",
    )
    config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Provider-specific configuration (API keys, etc.)",
    )
    is_active = models.BooleanField(default=True)

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_integration_type_display()})"


class AudienceIntegration(models.Model):
    """
    Links an Audience to an Integration with optional per-audience settings.
    When a subscriber is added to the audience, all active audience-integrations are executed.
    """

    audience = models.ForeignKey(
        "audiences.Audience",
        on_delete=models.CASCADE,
        related_name="integrations",
    )
    integration = models.ForeignKey(
        Integration,
        on_delete=models.CASCADE,
        related_name="audience_integrations",
    )
    settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Per-audience overrides or custom fields for this integration",
    )
    is_active = models.BooleanField(default=True)

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["audience", "integration"]]

    def __str__(self):
        return f"{self.audience.name} → {self.integration.name}"


class IntegrationLog(models.Model):
    """
    Logs the result of each integration execution for a subscriber.
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    subscriber = models.ForeignKey(
        "audiences.Subscriber",
        on_delete=models.CASCADE,
        related_name="integration_logs",
    )
    integration = models.ForeignKey(
        Integration,
        on_delete=models.CASCADE,
        related_name="logs",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    response_data = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.subscriber.email} → {self.integration.name}: {self.status}"
