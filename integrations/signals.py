from django.db.models.signals import post_save
from django.dispatch import receiver
from audiences.models import Subscriber


@receiver(post_save, sender=Subscriber)
def trigger_integrations(sender, instance, created, **kwargs):
    if created:
        # Import here to avoid circular dependency
        from integrations.tasks import process_subscriber_integrations

        # Queue async task (assuming Celery)
        process_subscriber_integrations.delay(instance.id)
