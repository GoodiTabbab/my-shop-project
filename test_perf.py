import os
import django
import sys
import time
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  
django.setup()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from shop.models import Order
from django.contrib.auth import get_user_model
from apscheduler.schedulers.blocking import BlockingScheduler

from shop.benchmarkers.base_audit import run_without_batch
from shop.benchmarkers.run_threads import run_with_threads
from shop.benchmarkers.run_thread_pool import run_with_thread_pool 
from shop.benchmarkers.run_workers import run_with_workers

def generate_huge_data():
    """Smart function to generate 50,000 dummy orders"""
    User = get_user_model()
    
    current_count = Order.objects.count()
    
    if current_count < 10000:
        print(f"⏳ Database contains only {current_count} orders.")
        
        first_user = User.objects.first()
        if not first_user:
            print(" No user found. Creating a default tester admin...")
            first_user = User.objects.create_user(username='tester_admin', password='password123')
            
        print(" Generating 50,000 dummy orders for stress testing... Please wait.")
        
        bulk_orders = [Order(cost=150.00, user=first_user) for _ in range(50000)]
        Order.objects.bulk_create(bulk_orders)
        
        print(f"✅ Data generated successfully! Total now: {Order.objects.count()} orders.")
    else:
        print(f"📊 Database is ready with {current_count} orders.")

def start_scheduled_benchmarks():
    """This function triggers at the scheduled time"""
    print(f"\n Scheduler triggered at: {datetime.now()}")
    print("====== Starting Nightly Batch Processing Benchmarks ======")
    
    run_with_threads(chunk_size=5000) 
    run_with_thread_pool(chunk_size=5000)
    run_with_workers(chunk_size=5000)
    
    print("\n========================================================")

if __name__ == '__main__':
    generate_huge_data()
    
    print("\n Launching Immediate Execution for Traditional Method...")
    run_without_batch()
    print(" Immediate execution finished successfully.")
    
    scheduler = BlockingScheduler()
    
    TARGET_HOUR = 10
    TARGET_MINUTE = 25
    
    print(f"\n Scheduler is running... Tasks (Threads & Workers) scheduled daily at {TARGET_HOUR:02d}:{TARGET_MINUTE:02d} AM.")
    print(" Leave this Terminal window open to run the scheduled background tasks...")
    
    scheduler.add_job(start_scheduled_benchmarks, 'cron', hour=TARGET_HOUR, minute=TARGET_MINUTE)
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n Scheduler stopped.")