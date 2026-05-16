import os
import django
import sys
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from shop.benchmarkers.run_thread_pool import run_with_thread_pool

def trigger_thread_pool():
    run_with_thread_pool(chunk_size=5000)

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    TARGET_HOUR = 15
    TARGET_MINUTE = 26
    
    print(f" Thread Pool scheduled daily at {TARGET_HOUR:02d}:{TARGET_MINUTE:02d} AM.")
    scheduler.add_job(trigger_thread_pool, 'cron', hour=TARGET_HOUR, minute=TARGET_MINUTE)
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n Scheduler stopped.")