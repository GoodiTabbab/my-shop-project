import os
import django
from apscheduler.schedulers.blocking import BlockingScheduler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings') 
django.setup()

from shop.benchmarkers.run_hybrid import run_with_hybrid_model

def trigger_hybrid():
    print("\n========================================================")
    print("⏰ Scheduler Triggered: Starting Hybrid Model Audit...")
    print("========================================================")
    
    run_with_hybrid_model(chunk_size=5000)
    
    print("\n========================================================")
    print("✨ Hybrid Scheduler Job Finished Successfully!")
    print("========================================================")

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    
    TARGET_HOUR = 11
    TARGET_MINUTE = 11
    
    scheduler.add_job(
        trigger_hybrid, 
        'cron', 
        hour=TARGET_HOUR, 
        minute=TARGET_MINUTE,
        id='trigger_hybrid_cron'
    )
    
    print("\n========================================================")
    print(" HYBRID MODEL SCHEDULER IS NOW LIVE")
    print("========================================================")
    print(f" Waiting to execute Hybrid Audit automatically at {TARGET_HOUR}:{TARGET_MINUTE} (24h format)")
    print(" Keep this Terminal window open...")
    print("========================================================")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n Scheduler stopped by user.")