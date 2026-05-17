import os
import django
import time
import psutil 
import threading
from concurrent.futures import ProcessPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')  
django.setup()

from shop.models import Order
from shop.benchmarkers.base_audit import process_worker_hybrid, save_benchmark_result

def get_memory_mb():
    try:
        main_process = psutil.Process(os.getpid())
        total_mem = main_process.memory_info().rss
        for child in main_process.children(recursive=True):
            try:
                total_mem += child.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return total_mem / (1024 * 1024)
    except Exception:
        return 0.0

def run_with_hybrid_model(chunk_size=5000):
    print("\n--- Starting: Batch Processing using (Hybrid Workers) ---")
    all_ids = list(Order.objects.values_list('id', flat=True))
    chunks = [all_ids[i:i + chunk_size] for i in range(0, len(all_ids), chunk_size)]
    
    start_time = time.time()
    start_mem = get_memory_mb()
    
    peak_mem = start_mem
    stop_monitoring = False

    def monitor_ram_loop():
        nonlocal peak_mem
        while not stop_monitoring:
            current_mem = get_memory_mb()
            if current_mem > peak_mem:
                peak_mem = current_mem
            time.sleep(0.05)

    monitor_thread = threading.Thread(target=monitor_ram_loop)
    monitor_thread.start()

    total_tax = 0
    try:
        with ProcessPoolExecutor(max_workers=4) as process_executor:
            futures = [process_executor.submit(process_worker_hybrid, chunk) for chunk in chunks]
            process_results = [f.result() for f in futures]
            total_tax = sum(process_results)
    finally:
        stop_monitoring = True
        monitor_thread.join()
        
    end_time = time.time()
    elapsed_time = end_time - start_time
    ram_usage = peak_mem - start_mem
    if ram_usage < 0: ram_usage = 0.5
    
    print(f" Real Peak RAM Consumption: {ram_usage:.2f} MB")
    
    save_benchmark_result(
        method_name="Hybrid Model (True Peak RAM)", 
        total_orders=len(all_ids), 
        total_sales=total_tax, 
        elapsed_time=elapsed_time, 
        ram_usage=ram_usage
    )
    return total_tax

def start_hybrid_scheduler_job():
    run_with_hybrid_model(chunk_size=5000)

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    TARGET_HOUR = 14
    TARGET_MINUTE = 40
    
    print(f" Waiting to execute Hybrid Audit automatically at {TARGET_HOUR:02d}:{TARGET_MINUTE:02d}")
    scheduler.add_job(start_hybrid_scheduler_job, 'cron', hour=TARGET_HOUR, minute=TARGET_MINUTE)
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n Scheduler stopped.")