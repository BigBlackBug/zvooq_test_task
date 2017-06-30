import logging

import redis
import requests
from celery import shared_task

_SERVICE_URL = "https://vast-eyrie-4711.herokuapp.com/?key={}"

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)

SECONDS_IN_DAY = 60 * 60 * 24

logger = logging.getLogger(__name__)


@shared_task
def service_request_task(key):
    logger.info("Started task for key {}".format(key))
    redis_client = redis.Redis(connection_pool=pool)
    # TODO if request takes too long, retry
    response = requests.get(_SERVICE_URL.format(key))
    logger.info(
        "Got response from the remote server: '{}'".format(response.content))
    if response.content == 'error':
        # TODO retry
        logger.error("Remote server returned an error")
    else:
        response_data = response.json()
        redis_client.set(key, response_data['hash'], ex=SECONDS_IN_DAY)
        redis_client.srem("in_progress", key)
