import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from shop.benchmarkers.base_audit import run_without_batch

if __name__ == '__main__':
    print("========================================================")
    print(" RUNNING: TRADITIONAL METHOD (ISOLATED PROCESS)         ")
    print("========================================================")
    run_without_batch()
    