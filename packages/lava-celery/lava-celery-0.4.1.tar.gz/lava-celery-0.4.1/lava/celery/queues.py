"""
lava.celery.queues
==================

Messaging declarations used by lava-celery
"""

from kombu import Exchange, Queue

# Exchange for streaming data
StreamExchange = Exchange(
    name='lava.celery.stream',
    type='direct',
    durable=False,
    auto_delete=False,
    delivery_mode='transient')

# Queue for getting per-client data
StreamQueue = Queue(
    exchange=StreamExchange,
    exclusive=True,
    durable=False)
