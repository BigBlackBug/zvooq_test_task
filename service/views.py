# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

import redis
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views import View

from service.tasks import service_request_task

logger = logging.getLogger(__name__)


class MainView(View):
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)

    def get(self, request):
        key = request.GET.get("key")
        if key is None:
            return JsonResponse(status=400, data={
                "error": "Key argument is missing"
            })
        logger.info("Got request for key {}".format(key))

        redis_client = redis.Redis(connection_pool=self.pool)

        logger.info("Checking if key {} is in cache".format(key))
        value = redis_client.get(key)
        if value:
            logger.info("Key {} is in cache. Value: {}".format(key, value))
            return JsonResponse({
                "hash": value
            })
        else:
            set_name = settings.REDIS_IN_PROGRESS_SET_NAME
            logger.info("Key {} not found in cache")
            if not redis_client.sismember(set_name, key):
                logger.info("Task for key {} is not running. "
                            "Starting.".format(key))
                redis_client.sadd(set_name, key)
                service_request_task.delay(key)
            # no content
            return HttpResponse(status=204)
