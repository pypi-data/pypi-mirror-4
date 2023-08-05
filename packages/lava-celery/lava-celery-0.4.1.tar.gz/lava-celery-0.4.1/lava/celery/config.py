"""
lava.celery.config
==================

This module contains hard-coded configuration for Celery
"""

import os
CELERY_IMPORTS = (
    'lava.celery.tasks',
)

BROKER_URL = os.getenv('BROKER_URL', 'amqp://guest:guest@localhost:5672//')

CELERY_RESULT_BACKEND = 'amqp'
