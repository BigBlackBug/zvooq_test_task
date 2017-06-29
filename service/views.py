# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.views import View


class MainView(View):
    def get(self, request):
        key = request.GET.get("key")
        return JsonResponse({
            "hash": "that's the key you've sent us '{}'".format(key)
        })
