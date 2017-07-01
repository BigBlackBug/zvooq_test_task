import logging

import redis
import requests
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.conf import settings
from requests import RequestException

_SERVICE_URL = "https://vast-eyrie-4711.herokuapp.com/?key={}"

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)

SECONDS_IN_DAY = 60 * 60 * 24
connect_timeout, read_timeout = 5.0, 10.0
logger = logging.getLogger(__name__)


@shared_task(bind=True, default_retry_delay=3, max_retries=5)
def service_request_task(self, key):
    def handle_retry(task):
        try:
            task.retry()
        except MaxRetriesExceededError:
            redis_client.srem(settings.REDIS_IN_PROGRESS_SET_NAME, key)
            logger.exception(e)

    logger.info("Started task for key {}".format(key))
    redis_client = redis.Redis(connection_pool=pool)
    try:
        response = requests.get(_SERVICE_URL.format(key),
                                timeout=(connect_timeout, read_timeout))
    except RequestException as e:
        handle_retry(self)
    else:
        logger.info(
            "Got response from the remote server: '{}'".format(
                response.content))
        if response.content == 'error':
            logger.error("Remote server returned an error")
            handle_retry(self)
        else:
            response_data = response.json()
            redis_client.set(key, response_data['hash'], ex=SECONDS_IN_DAY)
            redis_client.srem("in_progress", key)
