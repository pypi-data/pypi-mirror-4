from celery.task import task
from django.conf import settings

from funkymetrics.kissmetrics import KM


@task(max_retries=2, default_retry_delay=30, ignore_result=False)
def send_event(identity, action, props, **kwargs):

    try:

        km = KM(settings.KISS_API_KEY)
        km.identify(identity)
        km.record(action, props)

    except Exception as exc:

        # Try later
        send_event.retry(args=[identity, action, props], kwargs=kwargs, exc=exc)
