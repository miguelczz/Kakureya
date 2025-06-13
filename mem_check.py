import os
import psutil

process = psutil.Process(os.getpid())
mem = process.memory_info().rss / (1024 * 1024)
print(f"Uso de RAM actual: {mem:.2f} MB")
