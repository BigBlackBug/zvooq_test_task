from celery import shared_task


@shared_task
def service_request_task(key):
    pass
