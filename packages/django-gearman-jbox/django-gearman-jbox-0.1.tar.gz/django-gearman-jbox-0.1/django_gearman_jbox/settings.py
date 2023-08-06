from django.conf import settings

# gearman jobs servers
GEARMAN_CLIENT_SERVERS = getattr(settings, 'GEARMAN_CLIENT_SERVERS', ['127.0.0.1:4730'])
GEARMAN_WORKER_SERVERS = getattr(settings, 'GEARMAN_WORKER_SERVERS', ['127.0.0.1:4730'])
