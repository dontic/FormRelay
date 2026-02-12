from celery import shared_task
from audiences.models import Subscriber
from integrations.models import IntegrationLog
from integrations.registry import IntegrationRegistry


@shared_task
def process_subscriber_integrations(subscriber_id):
    subscriber = Subscriber.objects.get(id=subscriber_id)

    for audience_integration in subscriber.audience.integrations.filter(is_active=True):
        integration = IntegrationRegistry.get_integration(
            audience_integration.integration.integration_type,
            audience_integration.integration.config,
        )

        log = IntegrationLog.objects.create(
            subscriber=subscriber,
            integration=audience_integration.integration,
            status="pending",
        )

        try:
            result = integration.execute(subscriber, audience_integration.settings)
            log.status = "success"
            log.response_data = result
        except Exception as e:
            log.status = "failed"
            log.error_message = str(e)

        log.save()
