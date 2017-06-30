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
    logger.debug("Started task for key {}".format(key))
    redis_client = redis.Redis(connection_pool=pool)
    response_data = requests.get(_SERVICE_URL.format(key)).json()
    logger.debug(
        "Got response from the remote server: '{}'".format(response_data))
    # TODO if request takes too long, retry
    if 'hash' in response_data:
        redis_client.set(key, response_data['hash'], ex=SECONDS_IN_DAY)
    else:
        # TODO handle errors
        pass
    redis_client.srem("in_progress", key)