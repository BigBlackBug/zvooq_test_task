#!/bin/bash

echo Starting Gunicorn.
exec gunicorn zvook_test_task.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3