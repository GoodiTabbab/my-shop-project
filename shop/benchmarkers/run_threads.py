import threading
import time
from shop.models import Order
from shop.benchmarkers.base_audit import heavy_calculation, get_memory_usage
from shop.benchmarkers.base_audit import save_benchmark_result
def thread_worker(orders_chunk, results, index):
    chunk_tax = 0
    for order in orders_chunk:
        chunk_tax += heavy_calculation(order)
    results[index] = chunk_tax

def run_with_threads(chunk_size=5000):
    print("\n--- Starting: Batch Processing using (Threads) ---")    
    all_ids = list(Order.objects.values_list('id', flat=True))
    chunks = [all_ids[i:i + chunk_size] for i in range(0, len(all_ids), chunk_size)]
    
    threads = []
    results = [0] * len(chunks)
    
    start_time = time.time()
    start_mem = get_memory_usage()
    
    for i, id_chunk in enumerate(chunks):
        orders_chunk = list(Order.objects.filter(id__in=id_chunk))
        
        t = threading.Thread(target=thread_worker, args=(orders_chunk, results, i))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    total_tax = sum(results)
    end_time = time.time()
    end_mem = get_memory_usage()
    elapsed_time = end_time - start_time
    ram_usage = end_mem - start_mem
    print(" Threads audit completed.")
    print(f" Time Elapsed: {end_time - start_time:.2f} seconds")
    print(f" RAM Consumption: {end_mem - start_mem:.2f} MB")
    save_benchmark_result(
        method_name="Multi-Threading (10 Threads)", 
        total_orders=50000, 
        total_sales=total_tax, 
        elapsed_time=elapsed_time,         
        ram_usage=ram_usage          
    )
    return total_tax