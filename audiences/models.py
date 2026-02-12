from django.db import models


class Source(models.Model):
    domain = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.domain


class Audience(models.Model):
    AUDIENCE_TYPES = [
        ("waitlist", "Waitlist"),
        ("newsletter", "Newsletter"),
        ("contact_form", "Contact Form"),
    ]

    name = models.CharField(max_length=255)
    audience_type = models.CharField(max_length=50, choices=AUDIENCE_TYPES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Audiences"

    def __str__(self):
        return f"{self.name} ({self.get_audience_type_display()})"


class Subscriber(models.Model):
    audience = models.ForeignKey(
        Audience, on_delete=models.CASCADE, related_name="subscribers"
    )

    # Personal information
    email = models.EmailField()  # Email always required
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=255, blank=True)

    # For contact forms
    message = models.TextField(blank=True)
    custom_data = models.JSONField(default=dict, blank=True)

    # Meta
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["audience", "email"]]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.email} - {self.audience.name}"
