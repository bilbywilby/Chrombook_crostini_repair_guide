import psutil

# Function to check disk usage

def check_disk_usage(disk):

disk_usage = psutil.disk_usage(disk)

print(f"Disk {disk} usage:")

print(f" Total: {disk_usage.total / (1024**3):.2f} GB")

print(f" Used: {disk_usage.used / (1024**3):.2f} GB")

print(f" Free: {disk_usage.free / (1024**3):.2f} GB")

# Function to check memory usage

def check_memory_usage():

memory = psutil.virtual_memory()

print("Memory usage:")

print(f" Total: {memory.total / (1024**3):.2f} GB")

print(f" Available: {memory.available / (1024**3):.2f} GB")

print(f" Used: {memory.used / (1024**3):.2f} GB")

print(f" Percentage: {memory.percent}%")

# Function to check CPU usage

def check_cpu_usage():

cpu_usage = psutil.cpu_percent(interval=1)

print(f"CPU usage: {cpu_usage}%")

# Run the checks

check_disk_usage('/')

check_memory_usage()

check_cpu_usage()