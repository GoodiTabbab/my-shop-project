import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from shop.models import Order
from shop.benchmarkers.base_audit import heavy_calculation, get_memory_usage, save_benchmark_result

def thread_worker_inside_process(orders_chunk):
    """الخيوط الداخلية التي تعمل داخل العملية المعزولة"""
    chunk_tax = 0
    for order in orders_chunk:
        chunk_tax += heavy_calculation(order)
    return chunk_tax

def process_worker_hybrid(id_chunk):
    """الـ Worker المعزول: يقوم بجلب بياناته وتوزيعها على خيوط داخلية"""
    orders_chunk = list(Order.objects.filter(id__in=id_chunk))
    
    sub_chunk_size = 500
    sub_chunks = [orders_chunk[i:i + sub_chunk_size] for i in range(0, len(orders_chunk), sub_chunk_size)]
    
    total_process_tax = 0
    with ThreadPoolExecutor(max_workers=8) as thread_executor:
        results = thread_executor.map(thread_worker_inside_process, sub_chunks)
        total_process_tax = sum(results)
        
    return total_process_tax

def run_with_hybrid_model(chunk_size=5000):
    print("\n--- Starting: Batch Processing using (Hybrid Worker + Thread Pool) ---")
    all_ids = list(Order.objects.values_list('id', flat=True))
    chunks = [all_ids[i:i + chunk_size] for i in range(0, len(all_ids), chunk_size)]
    
    start_time = time.time()
    start_mem = get_memory_usage()
    
    with ProcessPoolExecutor(max_workers=4) as process_executor:
        process_results = process_executor.map(process_worker_hybrid, chunks)
        total_tax = sum(process_results)
        
    end_time = time.time()
    end_mem = get_memory_usage()
    
    elapsed_time = end_time - start_time
    ram_usage = end_mem - start_mem
    
    print(" Hybrid Model audit completed.")
    print(f" Time Elapsed: {elapsed_time:.2f} seconds")
    print(f" RAM Consumption: {ram_usage:.2f} MB")
    
    save_benchmark_result(
        method_name="Hybrid Model (4 Workers x 4 Threads)", 
        total_orders=len(all_ids), 
        total_sales=total_tax, 
        elapsed_time=elapsed_time, 
        ram_usage=ram_usage
    )
    return total_tax