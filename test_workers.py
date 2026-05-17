import os
import django
import sys
import time
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import psutil 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from shop.benchmarkers.base_audit import process_worker_pure, save_benchmark_result
from shop.models import Order
from concurrent.futures import ProcessPoolExecutor

def get_total_system_ram_mb():
    """تحسب الرام الحالي للعملية الرئيسية + جميع الـ Workers المنبثقة بدقة عالية"""
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

# ... (الحفاظ على بقية الاستيرادات ودوال الرام كما هي في كودك)

def run_with_workers_internal(chunk_size=5000):
    """توزيع المهام بعدالة عبر الـ IDs وتمريرها للعمليات"""
    from shop.models import Order
    
    # جلب الـ IDs لتصبح متطابقة تماماً مع طريقة عمل الخيوط والهايبر
    all_ids = list(Order.objects.values_list('id', flat=True))
    chunks = [all_ids[i:i + chunk_size] for i in range(0, len(all_ids), chunk_size)]    
    
    with ProcessPoolExecutor(max_workers=4) as process_executor:
        futures = [process_executor.submit(process_worker_pure, chunk) for chunk in chunks]
        process_results = [f.result() for f in futures]
        total_tax = sum(process_results)
        
    return total_tax

# ... (باقي كود الـ trigger_workers والمجدول يبقى كما هو دون تغيير)

def trigger_workers():
    print("\n========================================================")
    print(" Scheduler Triggered: Starting Pure Workers Audit...")
    print("========================================================")
    
    start_mem = get_total_system_ram_mb()
    start_time = time.time()
    
    import threading
    peak_mem = start_mem
    stop_monitoring = False

    def monitor_ram_loop():
        nonlocal peak_mem
        while not stop_monitoring:
            current_mem = get_total_system_ram_mb()
            if current_mem > peak_mem:
                peak_mem = current_mem
            time.sleep(0.05)  

    monitor_thread = threading.Thread(target=monitor_ram_loop)
    monitor_thread.start()

    total_tax = 0
    try:
        # استدعاء الدالة الداخلية المستقرة
        total_tax = run_with_workers_internal(chunk_size=5000)
    finally:
        stop_monitoring = True
        monitor_thread.join()

    end_time = time.time()
    elapsed_time = end_time - start_time
    
    real_ram_usage = peak_mem - start_mem
    if real_ram_usage < 0: real_ram_usage = 0.5  
    
    total_orders = Order.objects.count()

    print("\n========================================================")
    print("  OVERRIDING WITH TRUE MEASUREMENTS FOR REPORT")
    print("========================================================")
    print(f" Time Elapsed: {elapsed_time:.2f} seconds")
    print(f" Real Peak RAM Consumption: {real_ram_usage:.2f} MB")
    print(f" Initial RAM: {start_mem:.2f} MB -> Peak RAM: {peak_mem:.2f} MB")
    print("========================================================")
    
    save_benchmark_result(
        method_name="Pure Workers (4 Workers Pool with Real Peak RAM)", 
        total_orders=total_orders, 
        total_sales=total_tax if total_tax else 0, 
        elapsed_time=elapsed_time, 
        ram_usage=real_ram_usage
    )
    print("✨ Accurate Workers Report saved and isolated successfully!")
    print("========================================================\n")

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    
    TARGET_HOUR = 13
    TARGET_MINUTE = 56
    
    print("\n========================================================")
    print(" PURE WORKERS SCHEDULER: LIVE WITH TRUE RAM OVERRIDE")
    print("========================================================")
    print(f" Waiting to execute Workers Audit automatically at {TARGET_HOUR:02d}:{TARGET_MINUTE:02d} (24h format)")
    print(" Keep this Terminal window open...")
    print("========================================================\n")
    
    scheduler.add_job(trigger_workers, 'cron', hour=TARGET_HOUR, minute=TARGET_MINUTE)
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n Scheduler stopped.")