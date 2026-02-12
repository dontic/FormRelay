from rest_framework import serializers
from audiences.models import Audience, Source, Subscriber


class AudienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audience
        fields = ["name", "audience_type"]


class SubscriberSerializer(serializers.ModelSerializer):
    audience = AudienceSerializer()

    class Meta:
        model = Subscriber
        fields = [
            "id",
            "audience",
            "email",
            "first_name",
            "last_name",
            "phone",
            "message",
            "custom_data",
            "source",
            "created_at",
        ]
        read_only_fields = ["id", "source", "created_at"]

    def _get_or_create_audience(self, audience_data):
        """Get an existing audience or create a new one."""
        audience, _ = Audience.objects.get_or_create(
            name=audience_data["name"],
            audience_type=audience_data["audience_type"],
        )
        return audience

    def _get_or_create_source(self):
        """Get or create a Source from the request's Origin or Referer header."""
        request = self.context.get("request")
        if not request:
            return None

        origin = request.META.get("HTTP_ORIGIN") or request.META.get(
            "HTTP_REFERER", ""
        )
        if not origin:
            return None

        # Extract the domain from the origin/referer URL
        from urllib.parse import urlparse

        parsed = urlparse(origin)
        domain = parsed.netloc or parsed.path
        if not domain:
            return None

        source, _ = Source.objects.get_or_create(domain=domain)
        return source

    def create(self, validated_data):
        audience_data = validated_data.pop("audience")
        audience = self._get_or_create_audience(audience_data)
        source = self._get_or_create_source()
        subscriber = Subscriber.objects.create(
            audience=audience, source=source, **validated_data
        )
        return subscriber

    def update(self, instance, validated_data):
        audience_data = validated_data.pop("audience", None)
        if audience_data:
            instance.audience = self._get_or_create_audience(audience_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

