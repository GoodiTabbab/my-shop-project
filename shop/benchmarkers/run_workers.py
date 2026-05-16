import multiprocessing
import time
import django
from shop.benchmarkers.base_audit import heavy_calculation, get_memory_usage
from shop.benchmarkers.base_audit import save_benchmark_result
def worker_process(id_chunk):
    django.setup() 
    from shop.models import Order
    
    try:
        orders_chunk = list(Order.objects.filter(id__in=id_chunk))
        chunk_tax = 0
        for order in orders_chunk:
            chunk_tax += heavy_calculation(order)
        return chunk_tax
        
    except Exception as e:
        print(f" Worker failed critically on chunk: {e}")
        return 0  

def run_with_workers(chunk_size=5000):
    print("\n--- Starting: Batch Processing using (Workers) ---")
    from shop.models import Order
    
    all_ids = list(Order.objects.values_list('id', flat=True))
    chunks = [all_ids[i:i + chunk_size] for i in range(0, len(all_ids), chunk_size)]
    
    start_time = time.time()
    start_mem = get_memory_usage()
    
    num_workers = multiprocessing.cpu_count()
    
    with multiprocessing.Pool(processes=num_workers) as pool:
        results = pool.map(worker_process, chunks)
        
    total_tax = sum(results)
    end_time = time.time()
    end_mem = get_memory_usage()
    elapsed_time = end_time - start_time
    ram_usage = end_mem - start_mem
    print(" Workers audit completed.")
    print(f" Time Elapsed: {end_time - start_time:.2f} seconds")
    print(f" Main Process RAM Consumption: {end_mem - start_mem:.2f} MB")
    save_benchmark_result(
      method_name="Workers Method (Multi-Processing)", 
      total_orders=50000, 
      total_sales=total_tax, 
      elapsed_time=elapsed_time, 
      ram_usage=ram_usage
  )
    return total_tax