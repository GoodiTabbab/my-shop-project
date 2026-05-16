import threading
import psutil
import os
from prometheus_client import Gauge

THREAD_COUNT = Gauge(
    'django_active_threads',
    'Number of active Python threads'
)

CPU_USAGE = Gauge(
    'django_cpu_usage_percent',
    'Django process CPU usage percentage'
)

RAM_USAGE = Gauge(
    'django_memory_usage_percent',
    'Django process RAM usage percentage'
)

# Get the current Django process only
_process = psutil.Process(os.getpid())


def update_system_metrics():
    THREAD_COUNT.set(threading.active_count())
    CPU_USAGE.set(_process.cpu_percent())
    RAM_USAGE.set(_process.memory_percent())
