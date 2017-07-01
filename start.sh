#!/bin/bash

echo Starting Gunicorn.
export DJANGO_SETTINGS_MODULE=zvook_test_task.settings
exec gunicorn zvook_test_task.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3