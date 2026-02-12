import json

from django.contrib import admin
from django.http import JsonResponse
from django.urls import path

from integrations.models import Integration, AudienceIntegration, IntegrationLog
from integrations.registry import IntegrationRegistry


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    list_display = ["name", "integration_type", "is_active", "created_at"]
    list_filter = ["integration_type", "is_active"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at"]

    def get_urls(self):
        custom_urls = [
            path(
                "config-schema/<str:integration_type>/",
                self.admin_site.admin_view(self.config_schema_view),
                name="integration-config-schema",
            ),
        ]
        return custom_urls + super().get_urls()

    def config_schema_view(self, request, integration_type):
        """Return the config schema template as JSON for the given integration type."""
        schema = IntegrationRegistry.get_config_schema(integration_type)
        return JsonResponse({"schema": schema})

    def add_view(self, request, form_url="", extra_context=None):
        extra_context = extra_context or {}
        # Pre-compute all schemas so the JS can work without extra AJAX on page load
        schemas = {}
        for key in IntegrationRegistry.list_integrations():
            schemas[key] = IntegrationRegistry.get_config_schema(key)
        extra_context["config_schemas"] = json.dumps(schemas)
        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        schemas = {}
        for key in IntegrationRegistry.list_integrations():
            schemas[key] = IntegrationRegistry.get_config_schema(key)
        extra_context["config_schemas"] = json.dumps(schemas)
        return super().change_view(request, object_id, form_url, extra_context)


@admin.register(AudienceIntegration)
class AudienceIntegrationAdmin(admin.ModelAdmin):
    list_display = ["audience", "integration", "is_active", "created_at"]
    list_filter = ["is_active", "integration__integration_type"]
    search_fields = ["audience__name", "integration__name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = ["subscriber", "integration", "status", "created_at"]
    list_filter = ["status", "integration__integration_type"]
    search_fields = ["subscriber__email", "integration__name"]
    readonly_fields = ["created_at"]
