# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import os

import redis
from django.conf import settings
from django.http import JsonResponse
from django.views import View

from service.request_status import RequestStatus
from service.tasks import service_request_task

logger = logging.getLogger(__name__)


class MainView(View):
    pool = redis.ConnectionPool(host=os.environ.get("REDIS_HOST"),
                                port=os.environ.get("REDIS_PORT"),
                                db=os.environ.get("REDIS_DB"))

    def get(self, request):
        key = request.GET.get("key")
        if key is None:
            return JsonResponse(status=400, data={
                "status": RequestStatus.ERROR,
                "error": "Key argument is missing"
            })

        try:
            # TODO A workaround for non-ASCII symbols in the key
            key = key.encode('ascii')
        except UnicodeEncodeError:
            return JsonResponse(status=400, data={
                "status": RequestStatus.ERROR,
                "error": "Only ASCII keys are supported"
            })

        logger.info("Got request for key {}".format(key))

        redis_client = redis.Redis(connection_pool=self.pool)

        logger.info("Checking if key {} is in cache".format(key))
        value = redis_client.get(key)
        if value:
            logger.info("Key {} is in cache. Value: {}".format(key, value))
            return JsonResponse({
                "status": RequestStatus.SUCCESS,
                "hash": value
            })
        else:
            in_progress_set = settings.REDIS_IN_PROGRESS_SET_NAME
            logger.info("Key {} not found in cache")
            if not redis_client.sismember(in_progress_set, key):
                logger.info("Task for key {} is not running. "
                            "Starting.".format(key))
                redis_client.sadd(in_progress_set, key)
                service_request_task.delay(key)

                response_status = RequestStatus.ACCEPTED
            else:
                response_status = RequestStatus.IN_PROGRESS

            return JsonResponse(status=202, data={
                "status": response_status
            })
