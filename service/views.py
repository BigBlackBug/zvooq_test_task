# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

import redis
from django.http import JsonResponse, HttpResponse
from django.views import View

from service.tasks import service_request_task

logger = logging.getLogger(__name__)


class MainView(View):
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)

    def get(self, request):
        key = request.GET.get("key")
        logger.info("Got request for key {}".format(key))
        # TODO input validation
        redis_client = redis.Redis(connection_pool=self.pool)
        logger.info("Checking if key {} is in cache".format(key))
        hash = redis_client.get(key)
        if hash:
            logger.info("Key {} is in cache. Value: {}".format(key, hash))
            return JsonResponse({
                "hash": hash
            })
        else:
            logger.info("Key {} not found in cache")
            if not redis_client.sismember("in_progress", key):
                logger.info("Task for key {} is not running. "
                             "Starting".format(key))
                redis_client.sadd("in_progress", key)
                service_request_task.delay(key)
            return HttpResponse(status=204)
