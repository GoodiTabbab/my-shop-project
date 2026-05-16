import os
import django
import sys
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from shop.benchmarkers.run_threads import run_with_threads

def trigger_threads():
    run_with_threads(chunk_size=5000)

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    TARGET_HOUR = 17
    TARGET_MINUTE = 23
    
    print(f" Regular Threads scheduled daily at {TARGET_HOUR:02d}:{TARGET_MINUTE:02d} AM.")
    scheduler.add_job(trigger_threads, 'cron', hour=TARGET_HOUR, minute=TARGET_MINUTE)
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n Scheduler stopped.")