from django.contrib import admin
from audiences.models import Source, Audience, Subscriber


class SubscriberInline(admin.TabularInline):
    model = Subscriber
    extra = 0
    fields = ["email", "first_name", "last_name", "phone", "source", "created_at"]
    readonly_fields = ["created_at"]


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ["domain", "description", "created_at"]
    search_fields = ["domain"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Audience)
class AudienceAdmin(admin.ModelAdmin):
    list_display = ["name", "audience_type", "is_active", "created_at"]
    list_filter = ["audience_type", "is_active"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [SubscriberInline]


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ["email", "audience", "first_name", "last_name", "source", "created_at"]
    list_filter = ["audience", "source", "audience__audience_type"]
    search_fields = ["email", "first_name", "last_name"]
    readonly_fields = ["created_at", "updated_at"]
    raw_id_fields = ["audience", "source"]
