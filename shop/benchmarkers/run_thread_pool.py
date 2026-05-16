import time
from concurrent.futures import ThreadPoolExecutor
from shop.models import Order
from shop.benchmarkers.base_audit import heavy_calculation, get_memory_usage
from shop.benchmarkers.base_audit import save_benchmark_result
def chunk_worker(id_chunk):
    """الدالة التي يستلمها الخيط ليعالج دفعة كاملة من البيانات"""
    orders_chunk = list(Order.objects.filter(id__in=id_chunk))
    chunk_tax = 0
    for order in orders_chunk:
        chunk_tax += heavy_calculation(order)
    return chunk_tax

def run_with_thread_pool(chunk_size=5000):
    print("\n--- Starting: Fourth Method (Thread Pool Executor) ---")    
    all_ids = list(Order.objects.values_list('id', flat=True))
    chunks = [all_ids[i:i + chunk_size] for i in range(0, len(all_ids), chunk_size)]
    
    start_time = time.time()
    start_mem = get_memory_usage()
    
    max_threads = 4
    
    total_tax = 0
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        results = executor.map(chunk_worker, chunks)
        total_tax = sum(results)
        
    end_time = time.time()
    end_mem = get_memory_usage()
    elapsed_time = end_time - start_time
    ram_usage = end_mem - start_mem
    print(" Thread Pool audit completed.")
    print(f" Time Elapsed: {end_time - start_time:.2f} seconds")
    print(f" RAM Consumption: {end_mem - start_mem:.2f} MB")
    save_benchmark_result(
      method_name="ThreadPoolExecutor (4 Workers)", 
      total_orders=50000, 
      total_sales=total_tax, 
      elapsed_time=elapsed_time, 
      ram_usage=ram_usage
  )
    return total_tax